"""
genotree - open the interactive GUI for this tool.
"""

from src.cli_textual.textual_genotree import GenoTree

def cli_genotree(args):
	app = GenoTree()
	app.run()



if __name__ == "__main__":
	cli_genotree(None)
