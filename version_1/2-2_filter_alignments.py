#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Ronja Rösner

Gets an AliGROOVE score matrix, an alignment file, a maximum threshold and a locus id as inputs. 
Outputs table containing all values from the input matrix that are below the threshold with their
corresponding row and column names as well as an alignment file filtered for the threshold.
"""

import pandas as pd # type: ignore
import argparse


# add input arguments
parser = argparse.ArgumentParser()
parser.add_argument('-d', '--input_table' , dest='input_table' , type=str , default=None , required=True, help='input aligroove score matrix')
parser.add_argument('-a', '--input_alignment' , dest='input_alignment' , type=str , default=None , required=True, help='input alignment file')
parser.add_argument('-l', '--locus_id', dest='locus_id' , type=str, default=None , required=True, help='input locus id')
parser.add_argument('-t', '--threshold', dest='threshold', type=float, default=0.2, required=False, help='threshold value (default: 0.2)')
args, unknown = parser.parse_known_args()

# import matrix with all values for this locus from file
score_matrix = pd.read_csv(args.input_table,sep="\t",index_col=0)
# create filtered matrix with only values lower than or equal to the threshold
filtered_matrix = score_matrix.where(score_matrix <= args.threshold)

# the following 4 lines were written with the help of GPT-4
# Stack the filtered matrix to get row indices, column names, and values
low_values = filtered_matrix.stack().reset_index()
low_values.columns = ['Row', 'Column', 'Value']
low_values['Value'] = low_values['Value'].round(2)  # Round values to 2 decimals

# exit the program if no values are below the threshold
if low_values.empty:
	print(f"No values found below the threshold ({args.threshold}). Exiting.")
	exit(0)

# save low_values to file
with open(f"{args.locus_id}_{args.threshold}-values"+".csv","w") as file:
	low_values.to_csv(file, sep=';', index=False, header=['Column', 'Row', 'Value (rounded)'])
	print(f"Low values saved as {file.name}")

# save filtered alignment to output file
with open(args.input_alignment) as alignment_content, open(f"{args.locus_id}-{args.threshold}-filtered.fasta", "w") as new_alignment:
	# determines whether to write lines to output
	write_flag = True 
	for line in alignment_content:
		# check if the current line is a gene sequence name
		if line.startswith(">"):
			# get the name of the sequence
			item_id = line[1:].strip()
			 # set write_flag based on the presence of the gene sequence in low_values
			write_flag = item_id not in low_values 
		if write_flag:
			# write line to the output file
			new_alignment.write(line)
	
	print(f"Filtered alignment written to {new_alignment.name}")

