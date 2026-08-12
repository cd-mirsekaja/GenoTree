from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Footer, Header, Markdown, Button

from src.cli.cmd_docs import docstrings

class MainScreen(Screen):
	CSS_PATH = "tcss/screen_main.tcss"

	def compose(self) -> ComposeResult:
		yield Header()
		yield Markdown("# Welcome to GenoTree!")
		yield Markdown("GenoTree is a bioinformatics toolkit for the creation of phylogenetic trees from a dataset of genomes and genes. This is the GUI for the tool, but you can also interact with it using the command line! For more information on available commands, see below.")
		with Container(id = "app-grid"):
			with VerticalScroll(id = "left-pane"):
				yield Markdown("## Overview")
				yield Markdown("### Configuration")
				yield Markdown("GenoTree offers extensive configuration options to make it work in as many environments as possible. The configuration wizard allows you to set any required file paths, change SBATCH parameters and overwrite the database path.")
				yield Markdown("### Database Management")
				yield Markdown("The pipeline requires an internal database to work. This database includes taxonomic and ecological information on each genome as well as identifiers for various sites. After changing the genome dataset, the database must be updated before the pipeline can be launched again.")
				yield Markdown("### Lookup")
				yield Markdown("GenoTree includes this tool to quickly find basic taxonomic information on any scientific name. It fetches data via the public APIs of the World Register of Marine Species (WoRMS), the Global Biodiversity Information Facility (GBIF) and the Interim Register of Marine and Non-Marine Genera (IRMNG).")
			with VerticalScroll(id = "right-pane"):
				yield Markdown("## Quick Access")

				yield Markdown("## Commands")
				yield Markdown("### genotree run")
				yield Markdown(docstrings["run"])
				yield Markdown("### genotree docs")
				yield Markdown(docstrings["docs"])
				yield Markdown("### genotree db")
				yield Markdown(docstrings["db"])
				yield Markdown("### genotree lookup")
				yield Markdown(docstrings["lookup"])

		yield Footer()