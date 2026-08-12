"""
GenoTree: Perform a detailed phylogenetic analysis on a combined dataset of genomes and genes.

Usage: genotree <operation> [options]

Operations:
  configure		Set up config and SLURM parameters
  database		Manage and update the internal database
  docs			Show detailed documentation
  lookup		Look up taxonomic information for a species using the WoRMS database
  run			Run the pipeline

Options:
  -h, --help	Show help message for the specific operation and exit
"""

import argparse

# import internal package functions
from .cmd_genotree import cli_genotree
from .cmd_configure import cli_configure
from .cmd_database import cli_db
from .cmd_docs import cli_docs
from .cmd_lookup import cli_lookup
from .cmd_run import cli_run

## set the main parser
main_parser = argparse.ArgumentParser(
	prog = "genotree",
	description = "genotree <operation> [options] - phylogenetic analysis pipeline"
	)
main_parser.set_defaults(func = cli_genotree)

## subparser manager
subparsers = main_parser.add_subparsers(
	dest = "operation",
	help = "available operations"
	)

# parser for configuration
parser_configure = subparsers.add_parser("configure",
	help = "set up config",
	description = "Start an interactive assistant to set up the configuration file and SLURM parameters for running the genotree pipeline."
	)
parser_configure.set_defaults(func = cli_configure)

# parser for managing the database
parser_db = subparsers.add_parser("db",
	help = "manage internal database",
	description = "genotree db [options] - manage and update the internal database"
	)
parser_db.add_argument(
    "-f", "--file",
    action = "store",
    help = "path to a file containing a list of genome accession numbers",
    required = False
)
parser_db.add_argument(
	"-a", "--accession",
	action = "store",
	help = "a single genome accession number",
	required = False
)
parser_db.add_argument(
	"-m", "--mode",
	action = "store",
	choices = ["update", "add", "remove"],
	help = "operation to perform on the database",
	required = True
)
parser_db.set_defaults(func = cli_db)

# parser for the documentation
parser_docs = subparsers.add_parser("docs",
	help = "show documentation",
	description = "genotree docs [options] - detailed usage documentation"
	)
parser_docs.add_argument(
	"-o", "--operation",
	action = "store",
	choices = ["configure", "db", "docs", "run"],
	required = False
	)
parser_docs.set_defaults(func = cli_docs)

# parser for looking up taxonomic information
parser_lookup = subparsers.add_parser("lookup",
	help = "lookup species information",
	description = "genotree lookup - look up taxonomic information for a species using the WoRMS database"
	)
parser_lookup.set_defaults(func = cli_lookup)

# Parser for running the pipeline
parser_run = subparsers.add_parser("run",
	help = "run the pipeline",
	description = "Run any one section of the pipeline or the entire pipeline using the configuration file. Options: all, 1, 2, 3, 4."
	)
parser_run.add_argument(
	"section", 
	action = "store",
	choices = ["all", "1", "2", "3", "4"]
	)
parser_run.set_defaults(func = cli_run)

def main():
	args = main_parser.parse_args()

	if "func" in args:
		args.func(args)
	else:
		main_parser.print_help()


if __name__ == "__main__":
	main()