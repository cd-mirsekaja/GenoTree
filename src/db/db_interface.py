"""

"""
import asyncio
import sys, os
import pandas as pd
import sqlite3
from typing import Callable

from db.db_input_parser import DBInputParser

from src.const import DATABASE_SCHEMA, ROOT_DIR


class DBInterface():
	"""
	Class for handling database interactions.
	Args:
		db_path (str): Path to the database file.
		log (Callable): Logging function, defaults to print.
	"""
	
	def __init__(self, db_path: str, db_overwrite: bool, log: Callable = print) -> None:

		self.db_path = db_path
		self.conn = None
		self.cursor = None
		self.log = log

		self._initializeDB(db_overwrite)

	def readData(self):
		pass

	def insertData(self, table_name: str, df: pd.DataFrame) -> None:
		"""
		Insert new data into the database. Either replace or append to existing data, or fail if the table already exists.
		Args:
			table_name (str): Name of the table to insert data into.
			df (pandas.DataFrame): DataFrame with the new data. Must contain a column with the primary key defined in the database schema.
		"""

		if table_name not in DATABASE_SCHEMA:
			self.log(f"Error: Table '{table_name}' is not defined in the database schema.")
			return

		self._connect()

		# turn all columns into strings to avoid type issues
		df = df.map(str)
		df.to_sql(table_name, self.conn, if_exists='append', index=False)
		self.conn.commit()

		self._disconnect()

	def removeData(self):
		pass

	def readRow(self):
		pass

	def insertRow(self, primary_id, data):
		pass

	def removeRow(self, primary_id):
		pass


	def _connect(self) -> None:
		"""
		Open a connection to the database and create a cursor for query execution.
		"""
		try:
			self.conn = sqlite3.connect(self.db_path)
			self.cursor = self.conn.cursor()
		except sqlite3.Error as e:
			self.log(f"Error connecting to database: {e}")
			sys.exit(1)

	def _disconnect(self) -> None:
		"""
		Close the connection to the database.
		"""
		if self.conn:
			self.conn.close()
			self.cursor = None

	def _removeDB(self) -> None:
		"""
		Helper to remove an existing database file if required.
		"""
		if os.path.isfile(self.db_path):
			try:
				os.remove(self.db_path)
				self.log(f"Existing database '{self.db_path}' removed.")
			except OSError as e:
				self.log(f"Error removing existing database: {e}")
				sys.exit(1)

	def _initializeDB(self, replace_existing: bool) -> None:
		"""
		Helper to initialize an empty database with the specified schema.
		"""
		if replace_existing:
			self._removeDB()
		
		self._connect()
		
		for table_name, columns in DATABASE_SCHEMA.items():
			columns = ", ".join([f"{col_name} {col_type.upper()}" for col_name, col_type in columns.items()])
			table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"

			self.cursor.execute(table_query)
			self.conn.commit()

		self._disconnect()



def updateDB(db_path: str,
			 input_data: list,
			 overwrite_file: bool = False,
			 verify_names: bool = True,
			 log: Callable = print) -> None:
	input_parser = DBInputParser(log = log)

	data = asyncio.run(input_parser.fetchData(input_data, verify_names))

	db = DBInterface(db_path, overwrite_file, log)

	data_keys = data.columns

	for table_name in DATABASE_SCHEMA.keys():
		db_keys = DATABASE_SCHEMA[table_name].keys()
		# match keys in fetched data to database schema so only columns with data are inserted into the database
		matched_keys = [db_key for db_key in db_keys if any(data_key in db_key for data_key in data_keys)]
		db_data = data[matched_keys]

		db.insertData(table_name, db_data)

	log(f"Database at '{db_path}' updated successfully. Inserted {len(data)} entries.")


def main():
	test_file = f"{ROOT_DIR}/test/test.csv"
	test_list = ["GCA975310", "Bufo bufo"]

	test_db = f"{ROOT_DIR}/test/test.db"
	
	updateDB(test_db, test_list, True, True)
	updateDB(test_db, test_file, False, True)


if __name__ == "__main__":
	main()