#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Ronja Roesner

Tool for retrieving taxonomic and habitat information from a database using an accession number
"""

import argparse, sqlite3, os

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--acc_number' , dest = 'acc_number' , type = str , default= None , required= True, help = 'input accession number')
parser.add_argument('-d', '--database' , dest = 'library' , type = str , default= None , required= True, help = 'input sql database')
args, unknown = parser.parse_known_args()

db_file=args.library

# remove database file if toggle is set to 1, else print different statements
if os.path.isfile(db_file):
	# establishes connection to the database
	db_conn=sqlite3.connect(db_file)
	# creates new cursor object to interact with the database
	c=db_conn.cursor()
else:
	raise Exception('Database does not exist. Exiting.')

# function for finding the Index for the current Accession Number
def get_id(acc_number: str):
	query="SELECT IDX FROM ids WHERE AccessionNumber = ?"
	c.execute(query,(acc_number,))
	idx=c.fetchone()
	
	if idx!=None:
		return idx[0]
	else:
		return "not found"

# function for getting taxonomic information from the database
def get_taxonomy(idx: int):
	query="SELECT ScientificName, Authority, taxGroup FROM taxonomy WHERE IDX = ?"
	c.execute(query,(idx,))
	tax_tuple=c.fetchone()
	
	return(tax_tuple)

# function for getting the habitat information from the database
def get_habitats(idx: int):
	query="SELECT isMarine, isBrackish, isFresh, isTerrestrial FROM habitats WHERE IDX = ?"
	
	c.execute(query, (idx,))
	habitat_boolean=c.fetchone()
	
	habitat_names = ["marine", "brackish", "freshwater", "terrestrial"]
	habitat_list = [habitat_names[i] for i in range(len(habitat_boolean)) if habitat_boolean[i] == 1]
	
	if habitat_list!=[]:
		habitat_str=', '.join(map(str,habitat_list))
	else:
		habitat_str="habitats unknown"
	
	return habitat_str

idx=get_id(args.acc_number)

# execute the functions if the genome was found in the database
if idx!="not found":
	tax_tuple=get_taxonomy(idx)
	habitats=get_habitats(idx)
	
	out_str=(f"Index {idx} / {tax_tuple[0]} {tax_tuple[1]} - {tax_tuple[2]} ({habitats})\n")
else:
	out_str="genome not found in database"

# print output to the console for further processing
print(out_str)

# close the connection to the database
db_conn.close()