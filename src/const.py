
def getProjectRoot():
	"""
	Gets the project root directory, assuming this function is called
	from a file within the project, and that there's a 'pyproject.toml'
	file at the project root.
	"""
	from pathlib import Path
	# Start from THIS file's directory
	current_file = Path(__file__).resolve() # Using resolve to get an absolute path.
	# Go up directories until we find 'pyproject.toml'
	for parent in current_file.parents: # Iterate over every parent.
		if (parent / "src").exists(): # Checks if file exists
			return parent
	raise FileNotFoundError("Project root (with src) not found.")

ROOT_DIR = getProjectRoot()

PROJECT_VERSION = "0.1.5"

DATABASE_SCHEMA = {
	"taxonomy": {
		"IDX": 'text primary key',
		"tKingdom": 'text',
		"tPhylum": 'text',
		"tClass": 'text',
		"tOrder": 'text',
		"tFamily": 'text',
		"tGenus": 'text',
		"tSpecies": 'text',
		"tSubspecies": 'text',
		"ScientificName": 'text',
		"Authority": 'text',
		"Vernacular_ENG": 'text',
		"Vernacular_GER": 'text'
	},
	"identifiers": {
		"IDX": 'text primary key',
		"AccessionNumber": 'text',
		"usageKey": 'text',
		"IRMNG_ID": 'text',
		"AphiaID": 'text',
		"PESI_GUID": 'text'
	},
	"traits": {
		"IDX": 'text primary key',
		"isMarine": 'blob',
		"isBrackish": 'blob',
		"isFreshwater": 'blob',
		"isTerrestrial": 'blob',
		"isAllWater": 'blob',
		"isIntertidal": 'blob',
		"isExtinct": 'blob'
	}
}