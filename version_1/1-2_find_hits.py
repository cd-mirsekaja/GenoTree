#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The unmodified version of this script was part of the appendix for Hughes et al., 2018.

This script requires an input of an nhmmer-result file, formatted using the --tblout modifier. There also needs to be a genome reference formatted as .fasta passed to the program.
The input file should be named AccessionNumber-LocusID-table.txt, while the genome file should be named AccessionNumber.fasta. It is important that the spelling of both AccessionNumbers is identical.
"""

from __future__ import division
import re
from sys import argv
import argparse
#import Bio
from Bio import SeqIO # type: ignore
from Bio.Seq import Seq # type: ignore
from Bio.SeqRecord import SeqRecord # type: ignore


parser = argparse.ArgumentParser()
parser.add_argument('-i1', '--input1' , dest = 'input1' , type = str , default= None , required= True, help = 'Tabular output from nhmmer search')
parser.add_argument('-i2', '--input2' , dest = 'input2' , type = str , default= None , required= True, help = 'Input of genomic data')
args, unknown = parser.parse_known_args()


# Open the result from the nhmmer search
nhmmer = open(args.input1)
name = args.input1[:args.input1.rfind(".txt")]
taxon_id = name.split("-")[2].split("/")[1]
locus_id = name.split("-") [3]

# prepare empty variables
hits = []
filtered_hits = []


# Process lines of input, save lines that contain hits (they don't start with a '#'), and remove extra spaces  
for line in nhmmer:
	
	if line.startswith("#"):
	
		pass
	
	else:
		
		single_spaces = re.sub(" +"," ", line)
		
		hits.append(single_spaces)

nhmmer.close()


# If the file contains no hits

if len(hits) == 0:

	print("No hits found for locus " + locus_id)

# Process hits

else:
	print(f"{len(hits)} hits found for locus {locus_id}")

	reference = open("/nfs/data/zapp2497/genomes/raw_fasta/"+args.input2)
	
	ending = args.input2.split(".")[2]
	
	seq_dict = SeqIO.to_dict(SeqIO.parse(reference, ending))
	
	reference.close()


for line in hits:
	columns = line.split(" ")
	scaffold = columns[0]
	query_locus = columns[2]
	align_start = int(columns[6]) - 1
	align_end = int(columns[7]) - 1
	align_len = abs(align_start - align_end)
	bit_score = float(columns[13])
		
	if align_len >= 100 and bit_score >= 100:
		
		if align_start < align_end:
			
			seq_record = seq_dict[scaffold]
			
			seq_slice = seq_record.seq[align_start:align_end]
				
			new_seq_record = SeqRecord(seq_slice, id = taxon_id + "|" + query_locus + "|" + scaffold + "|" + str(align_start) + "|" + str(align_end), description = '')
			
			filtered_hits.append(new_seq_record)
		
		elif align_start > align_end:
			
			seq_record = seq_dict[scaffold]
			
			whole_seq = seq_record.seq
			
			seq_revcomp = whole_seq.reverse_complement()
			
			seq_length = len(whole_seq)
			
			new_start = seq_length - align_start -1
			
			new_end = new_start + align_start - align_end -1
			
			seq_slice = seq_revcomp[new_start:new_end]

			new_seq_record = SeqRecord(seq_slice, id = taxon_id + "|" + query_locus + "|" + scaffold + "|" + str(align_start) + "|" + str(align_end), description = '')
	
			filtered_hits.append(new_seq_record)	


if len(filtered_hits) > 0:
	
	myfasta = open(taxon_id + "-" + locus_id + "-hits" + ".fasta", "w")
	
	for entry in filtered_hits:
		
		myfasta.write(entry.format("fasta"))