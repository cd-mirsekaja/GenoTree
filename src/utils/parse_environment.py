import os

from src.utils.parse_configuration import ConfigParser

class EnvironmentParser:
	"""
	Class for generating environment files from the configuration file.
	Each run will create a file "global.env" with any variables that are required by multiple scripts in the pipeline, and a .env file for each script of each section that contains the SLURM parameters for that script.
	"""

	def __init__(self, config_file: str, envdir: str):
		config_parser = ConfigParser(config_file)
		self.config = config_parser.read()
		
		self.envdir = envdir

		self.sections = ["section_1", "section_2", "section_3"]
	
	def createFile(self, env_name: str, env_content: list):
		"""
		Creates a .env file with the given name and contents.
		Arguments:
            env_name (str) - env file name
			env_content (list) - list of strings to write, strings will be joined with newline characters
		"""

		env_path = os.path.join(self.envdir, env_name)
		with open(env_path, "w") as file:
			file.write("\n".join(env_content))

	def createGlobal(self):
		"""
		Creates a global environment file with all paths from the configuration file.
		"""

		paths = self.config["paths"]

		env_content = [
			"# paths",
			f"WORKDIR_ROOT={paths['workdir_root']}",
			f"OUTPUT_ROOT={paths['output_root']}",
			f"DATABASE={paths['input_database']}",
			f"INPUT_GENOMES={paths['input_genomes']}",
			f"INPUT_GENES={paths['input_genes']}",
			f"INPUT_ALIGNMENTS_RAW={paths['input_alignments_raw']}",
			f"INPUT_ALIGNMENTS_FILTERED={paths['input_alignments_filtered']}",
			f"INPUT_ALIGNMENTS_FINISHED={paths['input_alignments_finished']}",
			f"INPUT_TREES={paths['input_trees']}"
		]

		self.createFile("global.env", env_content)
	
	def createScript(self, section: str, script: str):
		"""
		Creates an environment file with all SLURM parameters for the specified section and script.

		Arguments:
		- section (str): name of the section (either "section_1", "section_2", or "section_3")
		- script (str): name of a script in the specified section
		"""

		base_params = self.config["sbatch_base"]
		script_params = self.config["sbatch_" + section][script]

		env_content = [
			"# base parameters",
			f"PARTITION={base_params['partition']}",
			f"MAIL_USER={base_params['mail-user']}",
			f"OUTPUT={base_params['output']}",
			f"ERROR={base_params['error']}",
			"",
			f"# parameters for {script}",
			f"CPUS_PER_TASK={script_params['cpus-per-task']}",
			f"MEM={script_params['mem']}",
			f"TIME={script_params['time']}",
			f"MAIL_TYPE={script_params['mail-type']}"
		]

		self.createFile(f"{script}.env", env_content)
	
	def createSection(self, section: str):
		"""
		Creates environment files for all scripts in the specified section.
		
		Arguments:
		- section (str): name of the section (either "section_1", "section_2", or "section_3")
		"""

		scripts = self.config["sbatch_" + section].keys()
		
		for script in scripts:
			self.createScript(section, script)
	
	def createEnvironment(self):
		"""
		Wrapper function to create all environment files.
		"""

		print("creating global environment file...")
		self.createGlobal()

		for section in self.sections:
			print(f"creating environment files for {section}...")
			self.createSection(section)
			
if __name__ == "__main__":
	config_path = "config/config_default.yaml"
	env_path = "config/env"

	env_parser = EnvironmentParser(config_path, env_path)
	env_parser.createEnvironment()