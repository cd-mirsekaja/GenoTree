"""
genotree docs [options] - comprehensive documentation for the GenoTree pipeline.

Options: 
  -o, --operation: Specify operation to show documentation for.

  choices:
	configure - documentation for the configuration assistant
	db - documentation for managing the internal database
	docs - documentation for the documentation
	run - documentation for running the pipeline
"""

# import and set docstrings for each command
from .cmd_configure import __doc__ as configure_docstring
from .cmd_database import __doc__ as db_docstring
from .cmd_lookup import __doc__ as lookup_docstring
from .cmd_run import __doc__ as run_docstring
docs_docstring = __doc__

docstrings = {
	"configure": configure_docstring,
	"db": db_docstring,
	"docs": docs_docstring,
	"lookup": lookup_docstring,
	"run": run_docstring,
}

all_doclist = [
	"\nGenoTree: Perform a detailed phylogenetic analysis on a combined dataset of genomes and genes.\n",
	"\n--------------------------------\n",
	configure_docstring,
	"\n--------------------------------\n",
	db_docstring,
	"\n--------------------------------\n",
	run_docstring,
	"\n--------------------------------\n",
	lookup_docstring,
	"\n--------------------------------\n",
	docs_docstring
]
all_docstring = "".join(all_doclist)

operations = {
	"configure": configure_docstring,
	"db": db_docstring,
	"docs": docs_docstring,
	"run": run_docstring,
	"all": all_docstring
}

# export function for the cli
def cli_docs(args):
	for operation, docstring in operations.items():
		if args.operation is None:
			print(all_docstring)
			break
		elif args.operation == operation:
			print(docstring)

if __name__ == "__main__":
	cli_docs(None)