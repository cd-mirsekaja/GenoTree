import httpx
import asyncio
from datetime import datetime
from typing import Literal

from src.db.db_merger import Merger


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

	out_name = scientific_name
	# handle httpx response
	if "names" in result.keys():
		best_result = result["names"][0]["bestResult"]
		# set the output name to the matched name
		out_name = best_result["currentCanonicalSimple"]

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
	import json

	sciname = "Ballerus ballerus"
	info = asyncio.run(getInfo(sciname, "Automatic", True))

	#sciname = input("Enter a scientific name: ")

	#verification = asyncio.run(verifySpeciesName(sciname, verbose = True))
	#print("Verification result:")
	#print(json.dumps(verification, indent = 2))

	print("Search result:")
	print(json.dumps(info, indent = 2))

