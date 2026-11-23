def getProjectRoot():
	import os
	from pathlib import Path
	d = Path(os.getcwd())
	found = 0
	while found == 0:
		if os.path.isfile(os.path.join(d, ".root_file")):
			found = 1
		else:
			d=d.parent
	return d


def getDatabasePath():
	"""
	Gets the correct path for the project database.
	"""
	import os
	p_data = "/data"
	p_db = "GenoTree_Database.db"
	db_path = f"{ROOT_DIR}{p_data}/{p_db}"
	
	return db_path

PROJECT_VERSION = "2026.0.10"
UI_THEME = "rose-pine"

ROOT_DIR = getProjectRoot()
DB_PATH = getDatabasePath()

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

FIELD_MAPPINGS = {
	"WoRMS": {
		'rank': 'Rank',
		'status': 'Status',
		'kingdom': 'tKingdom',
		'phylum': 'tPhylum',
		'class': 'tClass',
		'order': 'tOrder',
		'family': 'tFamily',
		'genus': 'tGenus',
		'scientificname': 'ScientificName',
		'isMarine': 'isMarine',
		'isBrackish': 'isBrackish',
		'isFreshwater': 'isFreshwater',
		'isTerrestrial': 'isTerrestrial',
		'isExtinct': 'isExtinct',
		'citation': 'Citation',
		'WoRMS_id': 'AphiaID'
	},
	"GBIF": {
		'rank': 'Rank',
		'taxonomicStatus': 'Status',
		'kingdom': 'tKingdom',
		'phylum': 'tPhylum',
		'class': 'tClass',
		'order': 'tOrder',
		'family': 'tFamily',
		'genus': 'tGenus',
		'canonicalName': 'ScientificName',
		'authorship': "Authority",
		'vernacularName': 'Vernacular_ENG',
		'GBIF_id': 'usageKey'
	},
	"IRMNG": {
		'rank': 'Rank',
		'status': 'Status',
		'kingdom': 'tKingdom',
		'phylum': 'tPhylum',
		'class': 'tClass',
		'order': 'tOrder',
		'family': 'tFamily',
		'genus': 'tGenus',
		'scientificname': 'ScientificName',
		'authority': 'Authority',
		'isMarine': 'isMarine',
		'isBrackish': 'isBrackish',
		'isFreshwater': 'isFreshwater',
		'isTerrestrial': 'isTerrestrial',
		'isExtinct': 'isExtinct',
		'citation': 'Citation',
		'IRMNG_id': 'IRMNG_ID'
	}
}