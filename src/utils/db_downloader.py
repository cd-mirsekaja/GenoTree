import json
import asyncio, httpx
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Callable, Literal

#import wikipediaapi as wiki
#from abc import ABC, abstractmethod

def get_project_root():
	"""
	Gets the project root directory, assuming this function is called
	from a file within the project, and that there's a 'pyproject.toml'
	file at the project root.
	"""
	# Start from THIS file's directory
	current_file = Path(__file__).resolve() # Using resolve to get an absolute path.
	# Go up directories until we find 'pyproject.toml'
	for parent in current_file.parents: # Iterate over every parent.
		if (parent / "src").exists(): # Checks if file exists
			return parent
	raise FileNotFoundError("Project root (with src) not found.")

ROOT_DIR = get_project_root()

class Downloader():
	def __init__(self, scientific_name: str, platforms: list = ["WoRMS", "GBIF", "IRMNG"]):
		"""
		Internal class for downloading data from multiple platforms:
		- WoRMS (World Register of Marine Species)
		- GBIF (Global Biodiversits Information Facility)
		- IRMNG (Interim Register of Marine and Nonmarine Genera)
		"""

		self.platforms = platforms
		# store scientific name as class variable
		self.scientific_name = scientific_name
		# modify scientific name for URL encoding
		self.scientific_name_mod = '%20'.join(scientific_name.split())
		# initialize empty ID variables
		self.aphia_id = None
		self.usagekey = None
		self.irmng_id = None

		# initialize URL snippets with information for ID retrieval
		self.request_url_snippets = self._loadURLSnippets()

	async def export(self):
		# construct ID URLs
		self.id_urls = self._constructTypeURL("id")
		# retrieve IDs and update ID variables
		self.ids = await self._getIDs()
		self.aphia_id = self.ids.get("WoRMS")
		self.usagekey = self.ids.get("GBIF")
		self.irmng_id = self.ids.get("IRMNG")

		# update URL snippets with retrieved IDs
		self.request_url_snippets = self._loadURLSnippets()

		# construct URLs for main data retrieval
		self.main_urls = self._constructTypeURL("main")
		# retrieve main data
		self.results = await self._getMainData()

		#self.vernacular_urls = self._constructTypeURL("vernacular")
		#self.vernaculars = await self._getVernaculars()

		return {
			"ids": self.ids,
			"results": self.results
			#"vernaculars": self.vernaculars
		}


	def _loadURLSnippets(self):
		url_snippets = {
				"WoRMS": {
					"id": {
						"url_base": "https://www.marinespecies.org/rest/AphiaIDByName/",
						"url_param": self.scientific_name_mod,
						"url_append": "?marine_only=false&extant_only=false"
					},
					"main": {
						"url_base": "https://www.marinespecies.org/rest/AphiaRecordByAphiaID/",
						"url_param": self.aphia_id,
						"url_append": ""
					},
					"vernacular": {
						"url_base": "https://www.marinespecies.org/rest/AphiaVernacularsByAphiaID/",
						"url_param": self.aphia_id,
						"url_append": ""
					}
				},
				"GBIF": {
					"id": {
						"url_base": "https://api.gbif.org/v1/species?name=",
						"url_param": self.scientific_name_mod,
						"url_append": "&offset=0&limit=1",
						"nested_keys": ['results', 0, 'key']
					},
					"main": {
						"url_base": "https://api.gbif.org/v1/species/",
						"url_param": self.usagekey,
						"url_append": ""
					},
					"vernacular": {
						"url_base": "https://api.gbif.org/v1/species/",
						"url_param": self.usagekey,
						"url_append": "/vernacularNames"
					}
				},
				"IRMNG": {
					"id": {
						"url_base": "https://www.irmng.org/rest/IRMNG_IDByName/",
						"url_param": self.scientific_name_mod,
						"url_append": ""
					},
					"main": {
						"url_base": "https://www.irmng.org/rest/AphiaRecordByIRMNG_ID/",
						"url_param": self.irmng_id,
						"url_append": ""
					},
					"vernacular": {
						"url_base": "https://www.irmng.org/rest/AphiaVernacularsByIRMNG_ID/",
						"url_param": self.irmng_id,
						"url_append": ""
					}
				}
			}
		
		requested_snippets = {}
		for platform in self.platforms:
			requested_snippets[platform] = url_snippets[platform]

		return requested_snippets

	def _constructTypeURL(self, url_type: str) -> dict:
		urls = {}
		for platform in self.request_url_snippets:
			snippet = self.request_url_snippets[platform][url_type]
			urls[platform] = f"{snippet['url_base']}{snippet['url_param']}{snippet['url_append']}"
		return urls

	def _getNestedValue(self, dictionary: dict, keys: list):
		for key in keys:
			dictionary = dictionary[key]
		return dictionary
	
	async def _getIDs(self):
		ids = {}
		async with httpx.AsyncClient() as client:
			for platform in self.id_urls:
				url = self.id_urls[platform]
				response = await client.get(url)
				try:
					result = response.json()
					if isinstance(result, dict):
						nest_level = self.request_url_snippets[platform]["id"]["nested_keys"]
						result = self._getNestedValue(result, nest_level)
					ids[platform] = result
				except Exception:
					ids[platform] = {"error": f"Failed to parse JSON from {url}"}
		return ids

	async def _getMainData(self):
		main_data = {}
		async with httpx.AsyncClient() as client:
			for platform in self.main_urls:
				url = self.main_urls[platform]
				response = await client.get(url)
				try:
					result = response.json()
					main_data[platform] = result
				except Exception:
					main_data[platform] = {"error": f"Failed to parse JSON from {url}"}
		return main_data

#	async def _getVernaculars(self):
#		vernaculars = {}
#		async with httpx.AsyncClient() as client:
#			for platform in self.vernacular_urls:
#				url = self.vernacular_urls[platform]
#				response = await client.get(url)
#				try:
#					result = response.json()
#					vernaculars[platform] = result
#				except Exception:
#					vernaculars[platform] = {"error": f"Failed to parse JSON from {url}"}
#		return vernaculars


class Merger():
	def __init__(self, scientific_name: str, platforms: list):
		"""
		Class for extracting and merging relevant values from downloaded dictionaries.
		"""
		self.downloader = Downloader(scientific_name, platforms)

	async def export(self):
		self.data = await self.downloader.export()
		self.ids = self.data.get("ids")
		self.results = self.data.get("results")
		#print(json.dumps(self.results, indent = 2))
		return self._mergeDicts()

	def _extractValues(self):
		fields = self._mapFields()
		results_mapped = {}
		for platform in self.results:
			results_mapped[platform] = {}
			for key_res, key_exp in fields[platform].items():
				if key_res in self.results[platform].keys():
					res = self.results[platform][key_res]
					if isinstance(res, str):
						res = res.capitalize() if key_exp != "Citation" and key_exp != "Authority" else res
					results_mapped[platform][key_exp] = res
		
		return results_mapped
	
	def _mergeDicts(self):
		extracted = self._extractValues()
		# merge all result dicts into a dataframe, turn that dataframe into a single dict
		merged_df = pd.DataFrame.from_dict(extracted, orient = "index")
		merged = merged_df.to_dict(orient = "list")

		def _normalizeContent(content: list, separator: str = " | "):
			normalized = []
			for value in content:
				if isinstance(value, str):
					value = value.strip()
					if value == "":
						continue
				if pd.isna(value):
					continue
				normalized.append(value)
			
			normalized = list(dict.fromkeys(normalized))

			if not normalized:
				return []
			
			if all(isinstance(value, str) for value in normalized):
				return separator.join(normalized)
			
			if all(isinstance(value, int) for value in normalized):
				return normalized[0] if len(normalized) == 1 else normalized
			
			return normalized

		for key, content in merged.items():
			# update the merged dictionary with the new data
			merged.update({key: _normalizeContent(content)})

		return(merged)

	def _mapFields(self):
		field_mappings = {
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
				'citation': 'Citation'
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
				'vernacularName': 'Vernacular_ENG'
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
				'citation': 'Citation'
			}
		}

		return field_mappings

async def verifySpeciesNameVerbose(scientific_name: str) -> dict:
	scientific_name_mod = '%20'.join(scientific_name.split())
	
	base_url = "https://verifier.globalnames.org/api/v1/search/"
	verifier_url = f"{base_url}n%3A{scientific_name_mod}"

	async with httpx.AsyncClient() as client:
		response = await client.get(verifier_url)
		try:
			result = response.json()
		except Exception:
			result = {"error": f"Failed to parse JSON from {verifier_url}"}
	
	# save relevant httpx results
	if "names" in result.keys():
		best_result = result["names"][0]["bestResult"]
		out_dict = {
			"matchType": best_result["matchType"],
			"curation": best_result["curation"],
			"SearchedName": scientific_name,
			"MatchedName": best_result["currentCanonicalSimple"]
		}
	# if no result, just return input name
	elif not "names" in result.keys():
		out_dict = {
			"matchType": None,
			"curation": None,
			"SearchedName": scientific_name,
			"MatchedName": None
		}
	
	# return full dictionary
	return out_dict

async def verifySpeciesName(scientific_name: str) -> str:
	scientific_name_mod = '%20'.join(scientific_name.split())
	
	base_url = "https://verifier.globalnames.org/api/v1/search/"
	verifier_url = f"{base_url}n%3A{scientific_name_mod}"

	async with httpx.AsyncClient() as client:
		try:
			response = await client.get(verifier_url)
			try:
				result = response.json()
			except Exception:
				result = {"error": f"Failed to parse JSON from {verifier_url}"}
		except Exception:
			result = {"error": f"Timeout with {verifier_url}"}
		
	
	# handle httpx response
	if "names" in result.keys():
		best_result = result["names"][0]["bestResult"]
		# set the output name to the matched name
		out_name = best_result["currentCanonicalSimple"]
	# if no result, just return input name
	elif not "names" in result.keys():
		# set the output name to the input
		out_name = scientific_name
	
	return out_name

async def getInfo(scientific_name: str, platform: Literal['Automatic', 'WoRMS', 'GBIF', 'IRMNG'] = 'Automatic', verify: bool = False) -> dict:
	if platform == "Automatic":
		platforms = ["WoRMS", "GBIF", "IRMNG"]
	else:
		platforms = [platform]

	# use species verification if requested
	if verify:
		verified_name = await verifySpeciesName(scientific_name)
		merger = Merger(verified_name, platforms)
	else:
		merger = Merger(scientific_name, platforms)

	# create an index from the input name. If no whitespace is in the name, only take the first three letters
	try:
		idx = f"{datetime.now().strftime('%y%m%d_%H%M')}.{scientific_name[:3]}_{scientific_name.split()[1][:3]}"
	except IndexError:
		idx = f"{datetime.now().strftime('%y%m%d_%H%M')}.{scientific_name[:3]}"


	# create dictionary with one entry
	out_dict = {
		"IDX": idx 
	}
	# update dictionary with the fetched data
	out_dict.update(await merger.export())

	return out_dict


if __name__ == "__main__":
	#scientific_name = input("Enter a scientific name: ")
	scientific_name = "Ballerus ballerus"

	#verification = asyncio.run(verifySpeciesName(scientific_name, verbose = True))
	#print("Verification result:")
	#print(json.dumps(verification, indent = 2))

	info = asyncio.run(getInfo(scientific_name, "Automatic", True))
	
	print("Search result:")
	print(json.dumps(info, indent = 2))

