import os
from pathlib import Path
from typing import Iterable

from textual import on
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, VerticalScroll, Horizontal
from textual.widget import Widget
from textual.widgets import Footer, Header, Markdown, Button, RichLog, Input, TextArea, TabbedContent, \
	Checkbox, ProgressBar, DataTable, Label, DirectoryTree, TabPane, OptionList, Select
from textual.validation import ValidationResult, Validator
from textual.reactive import reactive

from src.db.db_input_parser import DBInputParser
from src.db.db_interface import DBInterface
from src.const import ROOT_DIR, UI_THEME, DATABASE_SCHEMA

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
	delimiter_selected = reactive(";")

	def compose(self) -> ComposeResult:
		with VerticalScroll(id = "search-left-pane"):
			with Container(id = "search-settings-checkboxes"):
				yield Markdown("## Settings")
				yield Markdown("General settings regarding the search.")
				yield Checkbox("Overwrite existing database",
					tooltip = "If checked, the existing database will be deleted and a new one will be created. BE VERY CAREFUL WITH THIS!",
					value = False,
					id = "db-overwrite-check")
				yield Checkbox("Verify Species Names",
					tooltip = "Autocomplete for species name abbreviations, allows for fuzzy queries e.g. 'B. bubo Linn. 1700-'. This can lead to unexpected results if the query is not precise.",
					value = True,
					id = "verify-speciesname-check")
				with Horizontal():
					yield Label("Input delimiter: ")
					yield Select(options = [("Semicolon", ";"), ("Komma", ","), ("Tab", "\t")],
								 id = "delimiter-select",
								 prompt = "Select input delimiter...",
								 value = ";")
			
			with Container(id = "search-settings-input"):
				yield Markdown("## Data Input")
				yield Markdown("Choose a file with valid input data or clear the current input.")
				with Container(id = "search-settings-input-tree"):
					
					with Horizontal():
						yield Input(value = str(self.dir_path),
									placeholder = "Path to input file...",
									id = "input-path",
									validators = [
										DirValidator()
									])
						yield Button("Select", id = "button-upload", variant = "default", flat = True)
					yield FilteredDirectoryTree(self.dir_path)
				with Horizontal():
					yield Button("Clear Input", id = "button-clear-input", variant = "default", flat = True)
			
			with Container(id = "search-settings-run"):
				yield Markdown("## Run")
				yield Markdown("Test if the input can be correctly parsed or start the search.")
				with Horizontal():
					yield Button("Parse Input", id = "button-parse-input", variant = "primary")
					yield Button("Submit Input", id = "button-submit-input", variant = "success")

	def update_dirtree(self, new_path) -> None:
		self.query_one(FilteredDirectoryTree).path = new_path

	async def on_select_changed(self, event: Select.Changed) -> None:
		self.delimiter_selected = self.query_one(Select).value
		self.screen.query_one(SearchMiddlePane).query_one(TextArea).placeholder = f"AccessionNumber{self.delimiter_selected}ScientificName"

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
		elif event.button.id == "button-parse-input":
			await self.button_parse()
		elif event.button.id == "button-submit-input":
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
	
	async def button_parse(self):
		input_parser = DBInputParser(log = self.screen.query_one(SearchRightPane).update_log)
		input_text = self.screen.query_one(SearchMiddlePane).query_one("#input-batch", TextArea).text
		self.screen.query_one(SearchRightPane).reset_progress()
		
		parsed_input = await input_parser.parseInput(input_text, "textarea", delimiter = self.delimiter_selected)
		
		if parsed_input:
			self.screen.query_one(SearchRightPane).update_log("Parsed from Input:")
			for acn, scn in parsed_input:
				self.screen.query_one(SearchRightPane).update_log(f"{acn} - {scn}")
			self.screen.query_one(SearchRightPane).update_log(" ")
	
	async def button_submit(self):
		input_parser = DBInputParser(log = self.screen.query_one(SearchRightPane).update_log)
		input_text = self.screen.query_one(SearchMiddlePane).query_one("#input-batch", TextArea).text
		
		parsed_input = await input_parser.parseInput(input_text, "textarea", delimiter = self.delimiter_selected)
		
		if parsed_input:
			input_len = len(parsed_input)
			
			self.screen.query_one(SearchRightPane).reset_progress()
			self.screen.query_one(SearchRightPane).update_steps(input_len)
			
			self.screen.query_one(SearchRightPane).update_log(f"Fetching data for {input_len} entries...")
			fetched_data = await input_parser.fetchData(parsed_input, False)
			
			db_overwrite = self.query_one("#db-overwrite-check", Checkbox).value
			db = DBInterface(db_overwrite = db_overwrite,
				log = self.screen.query_one(SearchRightPane).update_log)
			db.updateDB(fetched_data)
			self.screen.query_one(SearchRightPane).update_log("Fetched data added to project database.")
			self.screen.query_one(SearchRightPane).update_log(" ")
			
			
			
class SearchMiddlePane(Widget):
	"""
	Widgets for the middle pane of the UI.
	"""
	def compose(self) -> ComposeResult:
		with Vertical(id = "search-middle-pane"):
			yield Label()
			with Container():
				yield Markdown("## Text Input")
				yield TextArea(placeholder = "AccessionNumber;ScientificName",
							   id = "input-batch")

class SearchRightPane(Widget):
	"""
	Widgets for the right pane of the UI.
	"""
	def compose(self) -> ComposeResult:
		with VerticalScroll(id = "search-right-pane"):
			yield Markdown("## Log")
			with Container():
				yield ProgressBar(show_eta = False)
				yield RichLog(highlight = True, markup = True, wrap = True)

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
		with Container(id = "search-app-grid"):
			yield SearchLeftPane()
			yield SearchMiddlePane()
			yield SearchRightPane()
	
	def on_mount(self):
		self.query_one(TextArea).focus()

class DBLeftPane(Widget):
	current_table = reactive("taxonomy")
	selected_cell = reactive
	
	def compose(self):
		with Vertical(id = "db-left-pane"):
			with Container(id = "db-options-container"):
				with Horizontal():
					yield Select(options = [("Taxonomy", "taxonomy"), ("Identifiers", "identifiers"), ("Traits", "traits")],
								 value = "taxonomy", prompt = "Select a table...")
					yield Input(id = "db-cell-input",
								placeholder = "Select a cell...",
								valid_empty = True,
								disabled = True)
			with VerticalScroll(id = "db-table-container"):
				yield DataTable(id = "db-table")
	
	def refreshDBTable(self):
		db = DBInterface(log = self.screen.query_one(DBRightPane).update_log)
		db_rows = db.readTable(self.current_table)
		db_cols = [*DATABASE_SCHEMA[self.current_table]]
		table = self.query_one(DataTable)
		table.clear(columns = True)
		table.add_columns(*db_cols)
		table.add_rows(db_rows)
		
	@on(Select.Changed)
	def select_changed(self, event: Select.Changed):
		self.current_table = str(event.value)
		self.refreshDBTable()
		# reset input field
		self.query_one(Input).clear()
		self.query_one(Input).disabled = True
		self.query_one(Input).placeholder = "Select a cell..."
	
	@on(DataTable.CellSelected)
	def datatable_cell_selected(self, event: DataTable.CellSelected):
		self.query_one(Input).clear()
		self.query_one(Input).disabled = False
		if not event.value is None:
			self.query_one(Input).insert(event.value, 0)
		else:
			self.query_one(Input).insert("", 0)
			self.query_one(Input).placeholder = ""
		
		self.selected_cell = event.cell_key
		self.query_one(Input).focus()
		
	@on(Input.Submitted)
	def input_submitted(self, event: Input.Submitted):
		table = self.query_one(DataTable)
		
		# get coordinates for the selected cell
		cell_coord = table.get_cell_coordinate(self.selected_cell.row_key, self.selected_cell.column_key)
		# update the DataTable widget
		table.update_cell_at(cell_coord, event.value, update_width = True)
		# update the database
		row_name = table.get_cell_at((cell_coord[0], 0))
		col_name = str([column.label for column in table.ordered_columns][cell_coord[1]])
		db = DBInterface(log = self.screen.query_one(DBRightPane).update_log)
		db.setCellByIDX(self.current_table, row_name, col_name, event.value)
		
		self.screen.query_one(DBRightPane).update_log(f"Updated cell at {cell_coord} to {event.value}")

class DBRightPane(Widget):
	def compose(self):
		with VerticalScroll(id = "db-right-pane"):
			yield Markdown("## Log")
			with Container():
				yield RichLog(highlight = True, markup = True, wrap = True)
	
	def update_log(self, update_text: str = "") -> None:
		if update_text != "":
			self.query_one(RichLog).write(update_text)


class DBPane(Widget):
	def compose(self):
		with Container(id = "db-app-grid"):
			yield DBLeftPane()
			yield DBRightPane()


class DatabaseScreen(Screen):
	"""
	Interface for the database management screen.
	"""

	CSS_PATH = "tcss/screen_database.tcss"

	def compose(self) -> ComposeResult:
		yield Header()
		yield Footer()

		with Container(id = "main-pane"):
			with TabbedContent(*["Fetch new data", "Edit current database"]):
				with Container():
					yield SearchPane()
				with Container():
					yield DBPane()
	
	@on(TabbedContent.TabActivated)
	async def tab_activated(self) -> None:
		self.query_one(DBPane).query_one(DBLeftPane).refreshDBTable()

class DatabaseApp(App):
	CSS_PATH = "tcss/textual_genotree.tcss"
	
	def on_ready(self) -> None:
		self.push_screen(DatabaseScreen())

	def on_mount(self) -> None:
		self.title = "GenoTree Database"
		self.sub_title = "manage the GenoTree Database"
		self.theme = UI_THEME


if __name__ == "__main__":
	app = DatabaseApp()
	app.run()
