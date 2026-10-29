"""

"""
import asyncio
import sys, os
import pandas as pd
from typing import Callable, Literal

from src.db.db_utils import getInfo

class DBInputParser():
	"""
	Class for handling data import. Can handle an input of a single accession number and scientific name, or a CSV file containing multiple entries. The output is a list of lists, where each inner list contains an accession number and a scientific name. If only one entry is provided, the output is a list of two elements: the accession number and the scientific name.
	"""

	def __init__(self, log: Callable = print) -> None:
		self.log = log

	async def parseInput(self, input_data, input_type: Literal['csv', 'textarea']) -> list:
		"""
		Get the parsed result.
		Returns:
			output (list) - list of parsed results
		"""

		if input_type == "csv":
			parsed_output = self._parseCSV(input_data)
		elif input_type == "textarea":
			parsed_output = self._parseTextArea(input_data)
		else:
			parsed_output = []

		return parsed_output

	async def fetchData(self, input_data: list, verify_names: bool) -> pd.DataFrame:
		"""
		Call on the Downloader to fetch data for all entries in the input list.
		"""

		data_list = []
		for entry in input_data:
			accession_number, scientific_name = entry

			try:
				data = await(getInfo(scientific_name, 'Automatic', verify=verify_names))
				data.update({'AccessionNumber': accession_number})

				data_list.append(data)
				self.log(f"Fetched data for {accession_number} ({scientific_name}).",
					update_step=1.0)
			except Exception:
				self.log(f"Data for {accession_number} ({scientific_name}) could not be fetched.")

		return pd.DataFrame(data_list)

	def _parseCSV(self, user_input: str, delimiter: str = ';') -> list[list[str]]:
		"""
		Parses genome accession numbers and scientific names from a CSV file.
		Args:
			user_input (str): Path to the input file.
			delimiter (str): Delimiter used in the CSV file.
		"""
		
		if not os.path.isfile(user_input):
			self.log(FileNotFoundError(f"File {user_input} does not exist."))
			sys.exit(1)
		
		if not user_input.endswith(".csv"):
			self.log(f"Error: File '{user_input}' is not a CSV file.")
			sys.exit(1)

		try:
			df = pd.read_csv(user_input, usecols = ["AccessionNumber", "ScientificName"], delimiter = delimiter)
		except:
			self.log(IndexError("Columns in input table do not match required schema."))
			sys.exit(1)
		
		return df.values.tolist()

	def _parseTextArea(self, user_input: str, delimiter: str = ';') -> list[list[str]]:
		"""
		Parses genome accession numbers and scientific names form a textual TextArea.
		Args:
			user_input (str): Text in the TextArea as string.
			delimiter (str): Delimiter used in the TextArea.
		"""

		input_list = user_input.split("\n")
		input_parsed = []
		for line in input_list:
			line_split = line.split(delimiter)
			if len(line_split) == 2:
				input_parsed.append(line_split)
			else:
				self.log(f"Error: {line} could not be parsed.")

			self.log(update_step = 1)

		return input_parsed
