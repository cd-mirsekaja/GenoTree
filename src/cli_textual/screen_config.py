from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Markdown, Button


class ConfigScreen(Screen):
	CSS_PATH = "tcss/screen_config.tcss"
	
	def compose(self) -> ComposeResult:
		yield Header()
		yield Markdown("# Configuration")
		yield Footer()
