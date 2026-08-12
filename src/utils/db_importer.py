"""

"""
import asyncio
import sys, os
import pandas as pd
from typing import Callable, Literal
	
from src.utils.db_downloader import ROOT_DIR, getInfo

class InputParser():
	"""
	Class for handling data import. Can handle an input of a single accession number and scientific name, or a CSV file containing multiple entries. The output is a list of lists, where each inner list contains an accession number and a scientific name. If only one entry is provided, the output is a list of two elements: the accession number and the scientific name.
	"""

	def __init__(self, input: str | list[str], input_type: Literal['csv', 'single'], log: Callable = print) -> None:
		self.log = log
		
		if input_type == "csv":
			self.output = self.parseCSV(input)
		elif input_type == "single":
			self.output = self.parseSingle(input)
		
	def export(self) -> list:
		"""
		Get the parsed result.
		Returns:
			output (list) - list of parsed results
		"""

		return self.output

	def parseSingle(self, input_list: list[str] = ["AccessionNumber", "ScientificName"]) -> list[list[str]]:
		"""
		Parses a single input of one accession number and one scientific name.
		"""

		if len(input_list) != 2:
			self.log("Error: Single input must contain exactly two elements: AccessionNumber and ScientificName.")
			sys.exit(1)
		
		return [input_list]

	def parseCSV(self, input_file: str, delimiter: str = ';') -> list[list[str]]:
		"""
		Imports genome accession numbers and scientific names from a CSV file.
		Args:
			input_file (str): Path to the input file.
			delimiter (str): Delimiter used in the CSV file.
		"""
		
		if not os.path.isfile(input_file):
			self.log(FileNotFoundError(f"File {input_file} does not exist."))
			sys.exit(1)
		
		if not input_file.endswith(".csv"):
			self.log(f"Error: File '{input_file}' is not a CSV file.")
			sys.exit(1)

		try:
			df = pd.read_csv(input_file, usecols = ["AccessionNumber", "ScientificName"], delimiter = delimiter)
		except:
			self.log(IndexError("Columns in input table do not match required schema."))
			sys.exit(1)
		
		return df.values.tolist()

class FetchData():
	"""
	
	"""

	def __init__(self, input_data: list, verify_names: bool, log: Callable = print) -> None:
		self.input_data = input_data
		self.verify_names = verify_names
		self.log = log
	
	def fetchAll(self) -> pd.DataFrame:
		"""
		Call on the Downloader to fetch data for all entries in the input list.
		"""

		data_list = []
		for entry in self.input_data:
			accession_number, scientific_name = entry
			
			data = asyncio.run(getInfo(scientific_name, 'Automatic', verify = self.verify_names))
			data.update({'AccessionNumber': accession_number})
			
			data_list.append(data)
			self.log(f"Fetched data for {accession_number} ({scientific_name}).")
		
		return pd.DataFrame(data_list)
	

def fetchData(input_data, input_type: Literal['csv', 'single'], verify_names: bool, log: Callable = print) -> pd.DataFrame:
	parser = InputParser(input_data, input_type, log)
	parsed_input = parser.export()
	fetcher = FetchData(parsed_input, verify_names, log)
	return fetcher.fetchAll()


def main():
	test_file = f"{ROOT_DIR}/test/test.csv"
	test_list = ["GCA975310", "Bufo bufo"]

	df = fetchData(test_file, "csv", False)
	#df = fetchData(test_list, "single", False)
	print(df)


if __name__ == "__main__":
	main()

