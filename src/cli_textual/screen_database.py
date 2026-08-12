from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, VerticalScroll, Horizontal
from textual.widget import Widget
from textual.widgets import Footer, Header, Markdown, Button, Log, Input, TextArea, Tabs, TabbedContent, ContentSwitcher, RadioSet, RadioButton, Checkbox, ProgressBar, DataTable, Label

from textual.reactive import reactive
from src.utils.db_interface import updateDB


class LeftPane(Widget):
	def compose(self) -> ComposeResult:
		with VerticalScroll(id = "left-pane"):
			yield Markdown("## Settings")
			yield Markdown("**Input Mode:**")
			with RadioSet():
				yield RadioButton("Single",
								  value = True,
								  tooltip = "Enter only a single accession number and scientific name.",
								  id = "input-single")
				yield RadioButton("Batch",
								  tooltip = "Enter a batch of scientific names.",
								  id = "input-batch")
			yield Checkbox("Overwrite existing database",
				tooltip = "If checked, the existing database will be deleted and a new one will be created. This is useful if you want to update the database after changing the genome dataset.",
				value = False)
			yield Checkbox("Verify Species Names",
				tooltip = "Autocomplete for species name abbreviations, allows for fuzzy queries e.g. 'B. bubo Linn. 1700-'. This can lead to unexpected results if the query is not precise.",
				value = True)
			yield Markdown("## Run")
			yield Button("Submit", id = "button-submit")

	async def on_radio_set_changed(self, event: RadioSet.Changed):
		self.screen.query_one(MiddlePane).query_one("#middle-content-switcher", ContentSwitcher).current = event.pressed.id

	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "button-submit":
			current_accession = self.screen.query_one(MiddlePane).query_one("#input-accession-number", Input).value
			current_sciname = self.screen.query_one(MiddlePane).query_one("#input-scientific-name", Input).value
			self.screen.query_one(RightPane).update_log(f"AccessionNumber: {current_accession}, ScientificName: {current_sciname}")
			self.screen.query_one(RightPane).update_progress(1)


class MiddlePane(Widget):
	def compose(self) -> ComposeResult:
		with Vertical(id = "middle-pane"):
			with TabbedContent(*["Input", "Overview"], id = "middle-tabs-main"):
				with Container():
					yield Label()
					with ContentSwitcher(initial = "input-single", id = "middle-content-switcher"):
						with Container(id = "input-single"):
							yield Input(placeholder = "Accession Number", id = "input-accession-number")
							yield Input(placeholder = "Scientific Name", id = "input-scientific-name")
						with Container(id = "input-batch"):
							yield TextArea(placeholder = "AccessionNumber; ScientificName")
				with Container():
					yield DataTable()



class RightPane(Widget):
	def compose(self) -> ComposeResult:
		with VerticalScroll(id = "right-pane"):
			yield Markdown("## Log")
			with Container():
				yield ProgressBar(total = self.screen.progress_steps)
				yield Log(highlight = True)

	def update_log(self, update_text: str) -> None:
		log = self.query_one(Log)
		log.write_line(update_text)

	def update_progress(self, update_step: int) -> None:
		progress = self.query_one(ProgressBar)
		progress.update(advance = update_step)

	def on_mount(self):
		self.update_log("Hello World!")
		self.update_log("This is an amazing test.")


class DatabaseScreen(Screen):
	CSS_PATH = "tcss/screen_database.tcss"

	progress_steps = reactive(100)

	def compose(self) -> ComposeResult:
		yield Header()
		yield Footer()

		yield Markdown("# Database")
		with Container(id = "app-grid"):
			yield LeftPane()
			yield MiddlePane()
			yield RightPane()
