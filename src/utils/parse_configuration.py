"""
Parser for configuration files in YAML format.

"""

import os, yaml

class ConfigParser:
	"""
	Class for parsing the configuration file for the genotree pipeline.

	Config structure:
	- paths: contains all input and output paths for the pipeline
	- sbatch_base: base parameters for all SLURM scripts
		partition: str
		mail-user: str
		output: str
		error: str
	- sbatch_section_x: parameters for each script in section x
		script_name:
			cpus-per-task: int
			mem: str
			time: str
			mail-type: str
	"""

	def __init__(self, config_file: str):
		self.config_file = config_file

		self.config_dict = {
			"paths": {
				"workdir_root": None,
				"output_root": None,
				"input_database": None,
				"input_genomes": None,
				"input_genes": None,
				"input_alignments_raw": None,
				"input_alignments_filtered": None,
				"input_alignments_finished": None,
				"input_trees": None,
			},
			"sbatch_base": {
				"partition": None,
				"mail-user": None,
				"output": None,
				"error": None
			},
			"sbatch_section_1": {
				"1_make_alignments": {
					"cpus-per-task": 8,
					"mem": "60G",
					"time": "0-64:00",
					"mail-type": "BEGIN, END, FAIL"
				},
				"1-1_process_genomes": {
					"cpus-per-task": 10,
					"mem": "80G",
					"time": "0-40:00",
					"mail-type": "FAIL"
				},
				"1-3_align_loci": {
					"cpus-per-task": 6,
					"mem": "60G",
					"time": "0-16:00",
					"mail-type": "FAIL"
				}
			},
			"sbatch_section_2": {
				"2_process_alignments": {
					"cpus-per-task": 8,
					"mem": "60G",
					"time": "0-24:00",
					"mail-type": "BEGIN, END, FAIL"
				},
				"2-1_rate_alignments": {
					"cpus-per-task": 10,
					"mem": "80G",
					"time": "0-20:00",
					"mail-type": "FAIL"
				}
			},
			"sbatch_section_3": {
				"3_make_trees": {
					"cpus-per-task": 8,
					"mem": "60G",
					"time": "0-24:00",
					"mail-type": "BEGIN, END, FAIL"
				},
				"3-1_make_gene_tree": {
					"cpus-per-task": 8,
					"mem": "60G",
					"time": "0-16:00",
					"mail-type": "FAIL"
				}
			}
		}
	
	def read(self):
		"""
		Reads the config file and returns a dictionary with the values.
		"""
		with open(self.config_file, 'r') as file:
			config = yaml.safe_load(file)
		return config

	def print(self, log = print):
		"""
		Prints the configuration to the console.
		"""
		config = self.read()
		
		yaml_str = yaml.dump(config, default_flow_style=False)
		log(f"Config at ./{self.config_file}:\n")
		log(yaml_str)

	def createDefault(self, overwrite = False):
		"""
		Creates a new config file with default values.
		"""
		if os.path.exists(self.config_file) and not overwrite:
			print(f"Config file already exists at {self.config_file}. Please verify that you want to overwrite it.")
			confirm_overwrite = input("Overwrite? [y/n]: ")
			if confirm_overwrite != "y":
				return
		
		with open(self.config_file, 'w') as file:
			yaml.dump(self.config_dict, file)

if __name__ == "__main__":
	config_path = "config/config_default.yaml"

	config_parser = ConfigParser(config_path)
	config_parser.createDefault()

	config_parser.print()