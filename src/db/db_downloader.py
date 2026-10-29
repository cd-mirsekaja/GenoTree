import json
import httpx

#import wikipediaapi as wiki
#from abc import ABC, abstractmethod

class DBDownloader():
	def __init__(self, scientific_name: str, platforms: list = ["WoRMS", "GBIF", "IRMNG"]):
		"""
		Downloads detailed information from multiple sources:
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
