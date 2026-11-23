"""
genotree lookup - find taxonomic information on any target group in an interactive GUI, fetched from either of these platforms: WoRMS, GBIF, IRMNG.
"""

from cli_textual.screen_lookup import LookupApp

def cli_lookup(args):
	app = LookupApp()
	app.run()


if __name__ == "__main__":
	cli_lookup(None)