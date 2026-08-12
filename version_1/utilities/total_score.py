#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Ronja Roesner

Tool for calculating the total mean and median scores for a given AliGROOVE table
"""

import re
import statistics
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file' , dest = 'file' , type = str , default= None , required= True, help = 'input scoring file')
parser.add_argument('-l', '--locus_id', dest = 'locus_id' , type = str , default= None , required= True, help = 'input locus id')
args, unknown = parser.parse_known_args()

# Read the text file
with open(args.file, 'r') as file:
    file_content = file.read()

# Find all values starting with '0.'
all_scores = re.findall(r'\b0\.\d+', file_content)

# Convert the extracted values from strings to floats
float_values = [float(val) for val in all_scores]

# Calculate the mean and median
mean_score = statistics.mean(float_values)
median_score = statistics.median(float_values)

outstring=f"{args.locus_id};{mean_score};{median_score}"

with open('total_scores.csv', 'a') as output_table:
    output_table.write("\n")
    output_table.write(outstring)

print(f"Scores for locus {args.locus_id}")
print(f"Mean: {mean_score}")
print(f"Median: {median_score}")