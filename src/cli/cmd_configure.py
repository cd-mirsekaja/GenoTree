"""
genotree configure - configuration assistant for the pipeline.

This command starts an interactive assistant to set up the configuration file. It will prompt the user to select which options they would like to change, then ask for new values.

Configuration options are:

"Path: working directory" - Path to root directory for the working directories. Working directories will be created at this location.
"Path: genome input" - Path to directory for genome input files. Genome files will be read from this location.
"Path: gene input" - Path to directory for gene input files. Gene files will be read from this location.
"Path: output" - Path to root directory for output files. Any directories for output files will be created at this location.
"""

import beaupy, os
from rich.console import Console

from src.utils.parse_configuration import ConfigParser

console = Console()

# dictionary with all possible config options
# keys:
# "q" = question to ask the user
# "a" = answer to show the user after input
# "v" = variable for the user input
prompt_options = {
	"Path: working directory":
	{
		"q": "Path to root directory for the working directories:",
		"a": "Working directories will be created at:",
		"v": None
	},
	"Path: genome input":
	{
		"q": "Path to directory for genome input files:",
		"a": "Genome files will be read from:",
		"v": None
	},
	"Path: gene input": 
	{
		"q": "Path to directory for gene input files:",
		"a": "Gene files will be read from:",
		"v": None
	},
	"Path: output": 
	{
		"q": "Path to directory for output files:",
		"a": "Output files will be written to:",
		"v": None
	}
}


# export function for the cli
def cli_configure(args):
	# set config file path - temporary, only for testing
	config_file = "config/config_test.yaml"

	config_parser = ConfigParser(config_file)

	console.print("Welcome to the configuration assistant for the GenoTree Pipeline!")

	# check if file exists, create default if not
	if not os.path.exists(config_file):
		config_parser.createDefault()

	# print current config to console if confirmed
	if beaupy.confirm("Print current configuration?"):
		config_parser.print(log = console.print)
	
	# reset config to default values if confirmed
	if beaupy.confirm("Reset current configuration to default values?"):
		config_parser.createDefault(overwrite = True)

	# modify config values if confirmed
	if beaupy.confirm("Modify current configuration?"):
		console.print("Please select which options you would like to change.")
		# present the user with list of all possible config options
		prompts_edit = beaupy.select_multiple(list(prompt_options.keys()))
		console.print(f"Editing:\n {prompts_edit}.")

		# for each selected option, prompt the user for input
		for key in prompts_edit:
			# store the user input in the prompt_options dictionary
			prompt_options[key]["v"] = beaupy.prompt(prompt_options[key]["q"])
			# return the user input in the console
			console.print(f"{prompt_options[key]['a']} {prompt_options[key]['v']}")

		console.print("Please select which sections to run by default:")
		sections_run = beaupy.select_multiple(["Section 1", "Section 2", "Section 3", "Section 4"])
		console.print(f"Selected sections: {sections_run}.")

if __name__ == "__main__":
	cli_configure(None)


