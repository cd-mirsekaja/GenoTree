"""
Contains various utility functions for interacting with the Downloader, Merger and Database interface.
"""

import httpx
from datetime import datetime
from typing import Literal

from src.db.db_merger import DBMerger

async def verifySpeciesName(scientific_name: str) -> str:
	"""
	Verify the input scientific name using the Global Names Architecture Scientific Names Services. (https://globalnames.org).
	"""

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

	out_name = scientific_name
	# handle httpx response
	if "names" in result.keys():
		best_result = result["names"][0]["bestResult"]
		# set the output name to the matched name
		out_name = best_result["currentCanonicalSimple"]

	return out_name


async def getInfo(scientific_name: str, platform: Literal['Automatic', 'WoRMS', 'GBIF', 'IRMNG'] = 'Automatic', verify: bool = False) -> dict:
	"""
	Fetch and merge data for the specified species name.
	Variables:
		- scientific_name (str): A scientific name, either at species level (most reliable) or any other taxonomic level.
		- platform (list | str): A platform to fetch data from, can be either of 'Automatic', 'WoRMS', 'GBIF' or 'IRMNG'. Defaults to 'Automatic'.
		- verify (bool): Whether to use the GNA name verifier on the input name before fetching the data. Defaults to 'False'.
	Returns:
		- dict: A dictionary of the downloaded data from any of the specified platforms.
	"""
	if platform == "Automatic":
		platforms = ["WoRMS", "GBIF", "IRMNG"]
	else:
		platforms = [platform]

	# use species verification if requested
	if verify:
		verified_name = await verifySpeciesName(scientific_name)
		merger = DBMerger(verified_name, platforms)
	else:
		merger = DBMerger(scientific_name, platforms)

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

