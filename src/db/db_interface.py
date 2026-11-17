import asyncio
import sys, os

import pandas as pd
import sqlite3
from typing import Callable

from src.db.db_input_parser import DBInputParser
from src.const import DATABASE_SCHEMA, DB_PATH


class DBInterface():
	"""
	Class for handling database interactions.
	Args:
		db_overwrite (Boolean): Whether to overwrite any existing database file on initialization. Defaults to 'False'.
		log (Callable): Logging function. Defaults to 'print'.
	"""
	
	def __init__(self, db_overwrite: bool = False, log: Callable = print) -> None:

		self.db_path = DB_PATH
		self.conn = None
		self.cursor = None
		self.log = log

		self._initializeDB(db_overwrite)

	def readColumns(self, table_name: str, cols: list) -> list:
		self._connect()
		sql_query = f"SELECT {', '.join(cols)} FROM {table_name}"
		self.cursor.execute(sql_query)
		
		rows = self.cursor.fetchall()
		self.conn.commit()
		self._disconnect()
		
		self.log(f"Fetched columns {cols} for table {table_name}.")
		
		return rows
	
	def readTable(self, table_name: str) -> list:
		self._connect()
		sql_query = f"SELECT * FROM {table_name}"
		self.cursor.execute(sql_query)
		
		rows = self.cursor.fetchall()
		self.conn.commit()
		self._disconnect()
		
		return rows

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
		# inject the new data into the specified table. append if the table already exists
		df.to_sql(table_name, self.conn, if_exists='append', index=False)
		self.conn.commit()

		self._disconnect()

	def setCellByIDX(self, table_name: str, idx: str, col_name: str, value: str):
		if table_name not in DATABASE_SCHEMA:
			self.log(f"Error: Table '{table_name}' is not defined in the database schema.")
			return
		sql_query = f"UPDATE {table_name} SET {col_name} = '{value}' WHERE IDX = '{idx}'"
		self._executeQuery(sql_query)

	def removeData(self):
		pass

	def readRow(self):
		pass

	def insertRow(self, primary_id, data):
		pass

	def removeRow(self, primary_id):
		pass
	
	def updateDB(self, input_data: pandas.DataFrame) -> None:
		
		data_keys = input_data.columns
		
		for table_name in DATABASE_SCHEMA.keys():
			db_keys = DATABASE_SCHEMA[table_name].keys()
			# match keys in fetched data to database schema so only columns with data are inserted into the database
			matched_keys = [db_key for db_key in db_keys if any(data_key in db_key for data_key in data_keys)]
			db_data = input_data[matched_keys]
			
			self.insertData(table_name, db_data)
		
		self.log(f"Database updated successfully. Inserted {len(input_data)} entries.")


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

	def _executeQuery(self, sql_query):
		self._connect()
		self.cursor.execute(sql_query)
		self.conn.commit()
		self._disconnect()
	
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


if __name__ == "__main__":
	name_list = [["GCA975310", "Bufo bufo"],
				 ["GCA123987", "Anguilla anguilla"],
				 ["GCA193748", "Vulpes vulpes"]]
	
	db = DBInterface(db_overwrite = True)
	
	input_parser = DBInputParser()
	data = asyncio.run(input_parser.fetchData(name_list, True))
	db.updateDB(data)
	
	print(db.readColumns("taxonomy", ["tKingdom", "tClass", "tOrder", "ScientificName"]))
	
	

	
	