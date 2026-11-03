import os
import pandas

from pathlib import Path
from typing import Iterable

from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, VerticalScroll, Horizontal
from textual.widget import Widget
from textual.widgets import Footer, Header, Markdown, Button, RichLog, Input, TextArea, TabbedContent, \
	Checkbox, ProgressBar, DataTable, Label, DirectoryTree, TabPane
from textual.validation import ValidationResult, Validator

from textual.reactive import reactive

from src.db.db_input_parser import DBInputParser
from src.db.db_interface import DBInterface
from src.const import ROOT_DIR

class DirValidator(Validator):
	"""Test if input is an existing directory."""
	def validate(self, value: str) -> ValidationResult:
		from pathlib import Path
		if Path(value).exists():
			if Path(value).is_dir():
				return self.success()
			else:
				return self.failure()
		else:
			return self.failure()

class FileValidator(Validator):
	"""Test if input is an existing file."""
	def validate(self, value) -> ValidationResult:
		from pathlib import Path
		if Path(value).exists():
			if Path(value).is_file():
				return self.success()
			else:
				return self.failure()
		else:
			return self.failure()

class FilteredDirectoryTree(DirectoryTree):
	"""
	Custom DirectoryTree widget filtering out any files that start with '.' or '__'
	"""
	def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
		return [path for path in paths if not path.name.startswith(".") and not path.name.startswith("__")]

class SearchLeftPane(Widget):
	"""
	Widgets for the left pane of the UI.
	"""

	dir_path = reactive(ROOT_DIR)
	path_selected = reactive

	def compose(self) -> ComposeResult:
		with VerticalScroll(id = "left-pane"):
			yield Markdown("## Settings")
			yield Markdown("General settings regarding the search.")
			yield Checkbox("Overwrite existing database",
				tooltip = "If checked, the existing database will be deleted and a new one will be created. This is useful if you want to update the database after changing the genome dataset.",
				value = False,
			   	id = "db-overwrite-check")
			yield Checkbox("Verify Species Names",
				tooltip = "Autocomplete for species name abbreviations, allows for fuzzy queries e.g. 'B. bubo Linn. 1700-'. This can lead to unexpected results if the query is not precise.",
				value = True,
				id = "verify-speciesname-check")

			yield Markdown("## Data Input")
			yield Markdown("Choose a file with valid input data or clear the current input.")
			yield Input(value = str(self.dir_path),
						placeholder = "Path to input file...",
						id = "input-path",
						validators = [
							DirValidator()
						])
			yield FilteredDirectoryTree(self.dir_path)
			with Horizontal():
				yield Button("Choose File", id = "button-upload", variant = "primary")
				yield Button("Clear Input", id = "button-clear-input", variant = "warning")
				yield Button("Clear Table", id = "button-clear-table", variant = "warning")

			yield Markdown("## Run")
			yield Markdown("Test if the input can be correctly parsed or start the search.")
			with Horizontal():
				yield Button("Parse Input", id = "button-parse", variant = "primary")
				yield Button("Submit Input", id = "button-submit", variant = "success")

	def update_dirtree(self, new_path) -> None:
		self.query_one(FilteredDirectoryTree).path = new_path

	async def on_tree_node_highlighted(self, event: FilteredDirectoryTree.NodeHighlighted):
		self.path_selected = event.node.data.__dict__.get("path")

	async def on_input_changed(self, event: Input.Changed) -> None:
		if event.validation_result.is_valid:
			self.update_dirtree(event.value)

	async def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "button-upload":
			await self.button_upload()
		elif event.button.id == "button-clear-input":
			await self.button_clear_input()
		elif event.button.id == "button-clear-table":
			await self.button_clear_table()
		elif event.button.id == "button-parse":
			await self.button_parse()
		elif event.button.id == "button-submit":
			await self.button_submit()
	
	async def button_upload(self):
		file_path = self.path_selected
		if not os.path.isfile(file_path):
			self.screen.query_one(SearchRightPane).update_log("Current selection is not a valid file.")
		else:
			with open(file = file_path, mode = "r") as file:
				lines = file.readlines()
				self.screen.query_one(SearchMiddlePane).query_one(TextArea).insert(''.join(lines))
		
		self.screen.query_one(SearchMiddlePane).query_one(TextArea).focus()
	
	async def button_clear_input(self):
		self.screen.query_one(SearchMiddlePane).query_one(TextArea).clear()
	
	async def button_clear_table(self):
		self.screen.query_one(SearchMiddlePane).query_one(DataTable).clear()
	
	async def button_parse(self):
		input_parser = DBInputParser(log = self.screen.query_one(SearchRightPane).update_log)
		input_text = self.screen.query_one(SearchMiddlePane).query_one("#input-batch", TextArea).text
		self.screen.query_one(SearchRightPane).reset_progress()
		
		parsed_input = await input_parser.parseInput(input_text, "textarea")
		
		if parsed_input:
			self.screen.query_one(SearchRightPane).update_log("Parsed from Input:")
			for acn, scn in parsed_input:
				self.screen.query_one(SearchRightPane).update_log(f"{acn} - {scn}")
	
	async def button_submit(self):
		input_parser = DBInputParser(log = self.screen.query_one(SearchRightPane).update_log)
		input_text = self.screen.query_one(SearchMiddlePane).query_one("#input-batch", TextArea).text
		
		parsed_input = await input_parser.parseInput(input_text, "textarea")
		
		if parsed_input:
			input_len = len(parsed_input)
			
			self.screen.query_one(SearchRightPane).reset_progress()
			self.screen.query_one(SearchRightPane).update_steps(input_len)
			
			self.screen.query_one(SearchRightPane).update_log(f"Fetching data for {input_len} entries...")
			fetched_data = await input_parser.fetchData(parsed_input, False)
			
			self.screen.query_one(SearchMiddlePane).update_table(fetched_data)
			self.screen.query_one(SearchRightPane).update_log("Fetched data added to overview table.")
			self.screen.query_one(SearchMiddlePane).query_one(TabbedContent).active = "search-overview"
			
			
			db_overwrite = self.query_one("#db-overwrite-check", Checkbox).value
			db = DBInterface(db_overwrite = db_overwrite,
				log = self.screen.query_one(SearchRightPane).update_log)
			db.updateDB(fetched_data)
			self.screen.query_one(SearchRightPane).update_log("Fetched data added to project database.")
			
			

class SearchMiddlePane(Widget):
	"""
	Widgets for the middle pane of the UI.
	"""
	def compose(self) -> ComposeResult:
		with Vertical(id = "middle-pane"):
			with TabbedContent():
				with TabPane("Input", id = "search-input"):
					yield Label()
					with Container():
						yield TextArea(placeholder = "AccessionNumber; ScientificName",
									   id = "input-batch")
				with TabPane("Overview", id = "search-overview"):
					yield DataTable(id = "overview-table")

	def reset_table(self):
		self.query_one(DataTable).clear()

	def update_table(self, df: pandas.DataFrame):
		# add results to overview table
		table = self.query_one(DataTable)
		if not table.columns:
			for col in df.columns.tolist():
				table.add_column(col)

		table.add_rows(list(df.itertuples(index=False, name=None)))


class SearchRightPane(Widget):
	"""
	Widgets for the right pane of the UI.
	"""
	def compose(self) -> ComposeResult:
		with VerticalScroll(id = "right-pane"):
			yield Markdown("## Log")
			with Container():
				yield ProgressBar(show_eta = False)
				yield RichLog(highlight = True, wrap = True)

	def update_log(self, update_text: str = "", update_step: float = 0.0) -> None:
		if update_text != "":
			self.query_one(RichLog).write(update_text)
		if update_step != 0.0:
			self.query_one(ProgressBar).advance(update_step)

	def update_steps(self, steps_total: float| None):
		self.query_one(ProgressBar).update(total = steps_total)

	def reset_progress(self):
		self.query_one(ProgressBar).update(total = None)
		self.query_one(ProgressBar).update(progress = 0.0)

class SearchPane(Widget):
	def compose(self):
		with Container(id="app-grid"):
			yield SearchLeftPane()
			yield SearchMiddlePane()
			yield SearchRightPane()


class DatabaseScreen(Screen):
	"""
	Interface for the database management screen.
	"""

	CSS_PATH = "tcss/screen_database.tcss"

	def compose(self) -> ComposeResult:
		yield Header()
		yield Footer()

		with Vertical(id = "main-pane"):
			with TabbedContent(*["Fetch new data", "Edit current database"]):
				with Container():
					yield SearchPane()
				with Container():
					yield Markdown("Database editing")


class DatabaseApp(App):
	def on_ready(self) -> None:
		self.push_screen(DatabaseScreen())

	def on_mount(self) -> None:
		self.title = "GenoTree Database"
		self.sub_title = "manage the GenoTree Database"


if __name__ == "__main__":
	app = DatabaseApp()
	app.run()
