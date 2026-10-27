"""
genotree db - manage the internal database for the pipeline

"""
from src.cli_textual.screen_database import DatabaseApp

def cli_db(args):
	app = DatabaseApp()
	app.run()

if __name__ == "__main__":
	cli_db(None)