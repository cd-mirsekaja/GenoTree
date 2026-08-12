from __future__ import annotations

from textual import getters, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll, Vertical, HorizontalScroll, Horizontal, Grid
from textual.reactive import reactive
from textual.screen import Screen, ModalScreen
from textual.widget import Widget
from textual.widgets import Input, Markdown, Footer, Header, RadioSet, RadioButton, Label, Static, Button

from .screen_lookup import LookupScreen
from .screen_main import MainScreen
from .screen_config import ConfigScreen		
from .screen_database import DatabaseScreen

class HelpScreen(ModalScreen):
	DEFAULT_CSS = """
	#dialog {
		grid-size: 2;
		grid-gutter: 1 2;
		grid-rows: 1fr 3;
		padding: 0 1;
		width: 60;
		height: 11;
		border: thick $background 80%;
		background: $surface;
	}

	#question {
		column-span: 2;
		height: 1fr;
		width: 1fr;
		content-align: center middle;
	}

	Button {
		width: 100%;
	}

	"""
	def compose(self) -> ComposeResult:
		yield Grid(
			Label("Help is coming, just hold out a little longer.", id = "question"),
			Button("Alright, I'll wait."),
			Button("I cannot wait any longer."),
			id = "dialog",
		)

	def on_button_pressed(self, event: Button.Pressed) -> None:
		self.app.pop_screen()

class QuitScreen(ModalScreen[bool]):
	DEFAULT_CSS = """
	#dialog {
		grid-size: 2;
		grid-gutter: 1 2;
		grid-rows: 1fr 3;
		padding: 0 1;
		width: 60;
		height: 11;
		border: thick $background 80%;
		background: $surface;
	}

	#question {
		column-span: 2;
		height: 1fr;
		width: 1fr;
		content-align: center middle;
	}

	Button {
		width: 100%;
	}

	"""
	BINDINGS = [
		("escape", "pop_screen", "ESC to close"),
	]
	def compose(self) -> ComposeResult:
		yield Grid(
			Label("Do you want to quit the GUI?", id = "question"),
			Button("Cancel", variant = "primary", id = "cancel"),
			Button("Quit", variant = "error", id = "quit"),
			id = "dialog",
		)
	# returns result of the button press to parent class
	def on_button_pressed(self, event: Button.Pressed) -> None:
		if event.button.id == "quit":
			self.dismiss(True)
		else:
			self.dismiss(False)

class GenoTree(App):
	CSS_PATH = "tcss/textual_genotree.tcss"

	SCREENS = {
		"main": MainScreen,
		"config": ConfigScreen,
		"database": DatabaseScreen,
		"lookup": LookupScreen
	}

	BINDINGS = [
		Binding(key = "question_mark", action = "help", description = "Help", key_display = "?"),
		#Binding(key = "ctrl+q", action = "request_quit", description = "Quit"),
		("ctrl+m", "switch_screen('main')", "Main Menu"),
		("ctrl+f", "switch_screen('config')", "Config"),
		("ctrl+d", "switch_screen('database')", "Database"),
		("ctrl+l", "switch_screen('lookup')", "Lookup"),
		]

	def action_help(self) -> None:
		self.push_screen(HelpScreen())

	# quit the app if requested by the user
	def action_request_quit(self) -> None:
		def check_quit(quit: bool | None) -> None:
			if quit:
				self.exit()
		
		self.push_screen(QuitScreen(), check_quit)

	def on_ready(self) -> None:
		self.push_screen(MainScreen())
	
	def on_mount(self) -> None:
		self.title = "GenoTree"
		self.sub_title = "An Interactive Phylogenetics Pipeline"
	

if __name__ == "__main__":
	app = GenoTree()
	app.run()