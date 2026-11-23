from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Markdown, Button


class PipelineScreen(Screen):
	CSS_PATH = "tcss/screen_pipeline.tcss"
	
	def compose(self) -> ComposeResult:
		yield Header()
		yield Footer()
		
		yield Markdown("# Pipeline")
