from __future__ import annotations

from textual import getters, work
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Input, Markdown, Footer, Header, RadioSet, RadioButton, Checkbox

from src.utils.db_downloader import getInfo

class Sidebar(Widget):
	def compose(self) -> ComposeResult:
		with VerticalScroll():
			yield Markdown("# Options")
			yield Markdown("## Search Platform...")
			with RadioSet(id = "focus_me"):
				yield RadioButton("Automatic",
					  tooltip = "Query all available platforms and combine the results.",
					  value = True)
				yield RadioButton("WoRMS",
					  tooltip = "Query the World Register of Marine Species.")
				yield RadioButton("GBIF",
					  tooltip = "Query the Global Biodiversity Information Facility.")
				yield RadioButton("IRMNG",
					  tooltip = "Query the Interim Register of Marine and Non-Marine Genera.")
			yield Markdown("## Search Parameters...")
			yield Checkbox("Verify Species Names",
				  tooltip = "Autocomplete for species name abbreviations, allows for fuzzy queries e.g. 'B. bubo Linn. 1700-'. This can lead to unexpected results if the query is not precise.",
				  value = True)

	async def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
		self.screen.selected_platform = event.pressed.label
		await self.screen.query_one(InputResults).on_options_updated()
	
	async def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
		self.screen.verify_species = event.value
		await self.screen.query_one(InputResults).on_options_updated()

class InputResults(Widget):
	results = getters.query_one("#results", Markdown)
	input = getters.query_one(Input)
	
	def compose(self) -> ComposeResult:
		yield Input(placeholder = "Search for a taxon name...", id = "species-search")
		with VerticalScroll(id = "results-container"):
			yield Markdown(id = "results")
	
	def on_mount(self):
		self.update_options()

	def update_options(self) -> None:
		self.platform = self.screen.selected_platform
		self.verify = self.screen.verify_species

	async def on_options_updated(self) -> None:
		self.update_options()

		if self.input.value:  # Re-lookup only if there's current input
			self.lookup_species(self.input.value)

	async def on_input_changed(self, message: Input.Changed) -> None:
		self.update_options()
		if message.value:
			self.lookup_species(message.value)
		else:
			await self.results.update("")
	
	@work(exclusive = True)
	async def lookup_species(self, species: str) -> None:
		results = await getInfo(species, self.platform, verify = self.verify)

		if species == self.input.value:
			markdown = self.make_species_markdown(results)
			self.results.update(markdown)

	def make_species_markdown(self, results: object) -> str:
		lines = []

		try:
			if results.get('Authority'):
				if results.get('Vernacular_ENG'):
					lines.append(f"# {results['ScientificName']} {results['Authority']} - {results['Vernacular_ENG']}")
				else:
					lines.append(f"# {results['ScientificName']} {results['Authority']}")
			else:
				if results.get('Vernacular_ENG'):
					lines.append(f"# {results['ScientificName']} - {results['Vernacular_ENG']}")
				else:
					lines.append(f"# {results['ScientificName']}")
			if results.get("Vernacular_EN"):
				lines.append(f"# {results['Vernacular_EN']}")
			if results.get('Status'):
				lines.append(f"**Status**: {results['Status']}\n")
			lines.append(f"**Rank**: {results['Rank']}\n")
			if results.get('tKingdom'):
				lines.append(f"**Kingdom**: {results['tKingdom']}\n")
			if results.get('tPhylum'):
				lines.append(f"**Phylum**: {results['tPhylum']}\n")
			if results.get('tClass'):
				lines.append(f"**Class**: {results['tClass']}\n")
			if results.get('tOrder'):
				lines.append(f"**Order**: {results['tOrder']}\n")
			if results.get('tFamily'):
				lines.append(f"**Family**: {results['tFamily']}\n")
			if results.get('tGenus'):
				lines.append(f"**Genus**: *{results['tGenus']}*\n")
			lines.append("---\n")
			if results.get('Citation'):
				citation = '\n'.join(results['Citation'].split(' | '))
				lines.append(f"`{citation}`")
		except KeyError:
			lines.append("No results found, sorry about that :3")
			return "\n".join(lines)

		return "\n".join(lines)


class LookupScreen(Screen):
	CSS_PATH = "tcss/screen_lookup.tcss"
	
	selected_platform = reactive("Automatic")
	verify_species = reactive(True)

	BINDINGS = [("ctrl+o", "toggle_sidebar", "Show Options")]
	show_sidebar = reactive(False)

	def action_toggle_sidebar(self) -> None:
		"""Toggle the sidebar visibility."""
		self.show_sidebar = not self.show_sidebar
	
	def watch_show_sidebar(self, show_sidebar: bool) -> None:
		"""Set or unset visible class when reactive changes."""
		self.query_one(Sidebar).set_class(show_sidebar, "-visible")
	
	def compose(self) -> ComposeResult:
		yield Header()
		yield Sidebar(id = "options-sidebar")
		yield InputResults()
		yield Footer()


class SpeciesLookup(App):
	def on_ready(self) -> None:
		self.push_screen(LookupScreen())
	
	def on_mount(self) -> None:
		self.title = "GenoTree Lookup"
		self.sub_title = "quickly find taxonomic information on any level"
	

if __name__ == "__main__":
	app = SpeciesLookup()
	app.run()
