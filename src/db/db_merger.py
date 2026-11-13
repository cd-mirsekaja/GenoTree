import pandas as pd

from src.const import FIELD_MAPPINGS
from src.db.db_downloader import DBDownloader

class DBMerger():
	def __init__(self, scientific_name: str, platforms: list):
		"""
		Merges downloaded data into a dictionary with standardized keys.
		Calls on the Downloader class.
		"""
		self.downloader = DBDownloader(scientific_name, platforms)

	async def export(self):
		self.data = await self.downloader.export()
		self.ids = self.data.get("ids")
		self.results = self.data.get("results")
		#print(json.dumps(self.results, indent = 2))
		return self._mergeDicts()

	def _extractValues(self):
		fields = FIELD_MAPPINGS
		results_mapped = {}
		for platform in self.results:
			results_mapped[platform] = {}
			for key_res, key_exp in fields[platform].items():
				if key_res in self.results[platform].keys():
					res = self.results[platform][key_res]
					if isinstance(res, str):
						res = res.capitalize() if key_exp != "Citation" and key_exp != "Authority" else res
					results_mapped[platform][key_exp] = res
				if key_res in self.ids.keys():
					res = self.ids[key_res]
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