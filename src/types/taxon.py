from src.const import DATABASE_SCHEMA

class Taxon:
	
	
	def __init__(self, name: str, taxonomy: dict, traits: dict):
		self.name = name
		
		self.tKingdom = taxonomy["tKingdom"] if "tKingdom" in taxonomy.keys() else None
		self.tPhylum = taxonomy["tPhylum"] if "tPhylum" in taxonomy.keys() else None
		self.tClass = taxonomy["tClass"] if "tClass" in taxonomy.keys() else None
		self.tOrder = taxonomy["tOrder"] if "tOrder" in taxonomy.keys() else None
		self.tFamily = taxonomy["tFamily"] if "tFamily" in taxonomy.keys() else None
		self.tGenus = taxonomy["tGenus"] if "tGenus" in taxonomy.keys() else None
		self.tSpecies = taxonomy["tSpecies"] if "tSpecies" in taxonomy.keys() else None
		self.tSubspecies = taxonomy["tSubspecies"] if "tSubspecies" in taxonomy.keys() else None
		self.ScientificName = taxonomy["ScientificName"] if "ScientificName" in taxonomy.keys() else None
		self.Authority = taxonomy["Authority"] if "Authority" in taxonomy.keys() else None
		