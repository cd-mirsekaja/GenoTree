#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Ronja Roesner

Tool for renaming genes in a FASTA file by replacing all pipe '|' symbols with a hyphen '-'
"""

import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file' , dest = 'file' , type = str , default = None , required = True, help = 'input file')
parser.add_argument('-d', '--directory', dest = 'out_dir', type = str, default = None, required = True, help = 'output directory')
args, unknown = parser.parse_known_args()

locus_id = args.file.split("-")[0] if not '/' in args.file else args.file.split("/")[-1].split("-")[0]
ending = args.file.split(".")[-1]


with open(args.file, 'r') as file:
	file_content = file.read()

# the following function was written with the help of ChatGPT
def transform_content(file_content):
    # Define the regex pattern for the transformation
    pattern = r"([A-Za-z0-9_]+\.\d+)\|[^|]+\|([A-Za-z0-9_.]+)\|(\d+)\|(\d+)"
    replacement = r"\1-\2-\3-\4"  # Replacement pattern using captured groups

    # Apply re.sub to replace all occurrences in the file content
    transformed_content = re.sub(pattern, replacement, file_content)

    return transformed_content

if ending=="fasta":
    file_content = transform_content(file_content)
elif ending=="treefile":
    file_content = re.sub(r'\|locus_E\d+-NoDups_OK\|[^:]+:', ':', file_content)
else:
    raise TypeError("file type not recognized")

with open(args.out_dir+'/'+locus_id+"-renamed." + ending,"w") as file_out:
    file_out.write(file_content)