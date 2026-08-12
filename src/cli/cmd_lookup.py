"""
genotree lookup - find taxonomic information on any target group in an interactive GUI, fetched from either of these platforms: WoRMS, GBIF, IRMNG.
"""

from src.cli_textual.screen_lookup import SpeciesLookup

def cli_lookup(args):
	app = SpeciesLookup()
	app.run()


if __name__ == "__main__":
	cli_lookup(None)