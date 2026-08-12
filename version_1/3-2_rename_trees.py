#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Ronja Roesner

Script for renaming the tips of phylogenetic trees with the corresponding index from the database
"""

import argparse, sqlite3, os, re

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--tree' , dest = 'tree_file' , type = str , default= None , required= True, help = 'input treefile')
parser.add_argument('-d', '--database' , dest = 'library' , type = str , default= None , required= True, help = 'input sql database')
parser.add_argument('-l', '--locus_id', dest = 'locus_id', type = str, default = None, required = False, help = 'input locus id')
parser.add_argument('-o', '--out_dir', dest = 'out_dir', type = str, default = None, required = False, help = 'input output folder')
args, unknown = parser.parse_known_args()

locus_id = args.tree_file.split("-")[0] if not args.locus_id else args.locus_id
out_dir = args.out_dir if args.out_dir else ""
db_file = args.library

# remove database file if toggle is set to 1, else print different statements
if os.path.isfile(db_file):
	# establishes connection to the database and creating an empty file if there is none
	db_conn = sqlite3.connect(db_file)
	# creates new cursor object to interact with the database
	c = db_conn.cursor()
else:
	raise Exception('Database does not exist. Exiting.')


# writes contents of input tree to variable treefile_content
with open(args.tree_file, 'r') as file:
	treefile_content = file.read()

# set variables for counting and creating a list of genomes
genome_count = 0
genome_list = []

# query to get the index and accession number from the database
query="SELECT IDX, AccessionNumber FROM ids"
c.execute(query)
# iterates over the rows of the query result to replace the accession number with the index
for row in c:
	idx,acc_number = row
	replacement_str = f"{idx}"
	
	if acc_number in treefile_content:
		treefile_content = treefile_content.replace(acc_number, replacement_str)
		genome_list.append(acc_number)
		genome_count = genome_count+1

# converts the list of genomes to a string
genome_string = str(genome_list)

# replaces all unneccessary clutter in the treefile with ":"
# catch gene names in the consensus supertrees
treefile_content = re.sub(r'-[A-Za-z0-9_.]+-?\d*-\d+-\d+:', ':', treefile_content)
# catch gene names in the cryptochrome gene trees
treefile_content = re.sub(r'__g\d+_t1_ORF_\d+:', ':', treefile_content)
treefile_content = re.sub(r'__TRINITY_DN\d+_c\d+_g\d+_i\d+_len_\d+_path__[\w-]+__ORF_\d+:', ':', treefile_content)
treefile_content = re.sub(r'__sprottn3_rep_c\d+____cov_[\d_]+_len_\d+_gc_[\d_]+_nseq_\d+_ORF_\d+:', ':', treefile_content)

# closes connection to the database
db_conn.close()

# writes treefile_content to new file
with open(out_dir + locus_id + "-" + str(genome_count) + "_genomes-renamed" + ".treefile","w") as tree_out:
	tree_out.write(treefile_content)
	print("Renamed treefile saved to ", tree_out.name)

with open(out_dir+"genome_list"+".log","a") as outfile:
	outfile.write('\n')
	outfile.write(args.tree_file+": " + str(genome_count) + " genomes")
	outfile.write('\n')
	outfile.write(genome_string)
	
	print("List of genomes saved to ",outfile.name)

