# genotree

Pipeline for making phylogenetic trees out of a dataset of genomes and exons. The scripts are written to run on a high performance cluster using SLURM.
The pipeline consists of multiple scripts working together. Input files and folders are set inside the scripts.


**Main Pipeline:**

[1_make_alignments.sh](1_make_alignments.sh)
- calls 1-1_process_genomes.sh, 1-3_align_loci.sh and utilities/speciesinfo.py
- Creates working directory and required subfolders while running.


[1-1_process_genomes.sh](1-1_process_genomes.sh)
- calls 1-2_find_hits.py
- finds hits for each locus in specified genome file.


[1-2_find_hits.py](1-2_find_hits.py)
- uses nhmmer-tables to create fasta files that contain hits for each locus


[1-3_align_loci.sh](1-3_align_loci.sh)
- aligns hits for specified locus.


[2_process_alignments.sh](2_process_alignments.sh)
- calls 2-1_rate_alignments.sh, 2-2_filter_alignments.py and utilities/total_score.py
- generates AliGROOVE-Scores for all alignments and returns .fasta-files that are filtered to not contain any sequences with a score below the supplied threshold (0.35)


[2-1_rate_alignments.sh](2-1_rate_alignments.sh)
- generates AliGROOVE matrices with similarity scores for all sequence alignments.


[2-2_filter_alignments.py](2-2_filter_alignments.py)
- filters the supplied sequence alignments for the score threshold


[3_make_trees.sh](3_make_trees.sh)
- calls 3-1_rename_trees.py
- creates individual phylogenetic trees from the supplied alignments and combines them into a supertree


[3-1_rename_trees.py](3-1_rename_trees.py)
- renames tree tips to make postprocessing easier


[4_color_trees.R](4_color_trees.R)
- calls 4-3_functions.R and 4-1_load_trees.R
- gets a phylogenetic tree and makes several differently annotated versions of it that get saved as pdfs or jpegs.


[4-1_compare_trees.R](4-1_compare_trees.R)
- calls 4-3_functions.R and 4-1_load_trees.R
- gets multiple phylogenetic trees and makes tanglegrams out of them


[4-2_load_trees.R](4-1_load_trees.R)
- contains the preamble for 4_color_trees.R to load phylo and plot trees into the workspace


[4-3_functions.R](4-3_functions.R)
- provides a multitude of custom functions for tree annotation


**Utilities:**

[speciesinfo.py](utilities/speciesinfo.py) - gets general information for specified taxon

[total_score.py](utilities/total_score.py) - calculates total mean and median scores for supplied AliGROOVE matrices

[align_cry.sh](utilities/align_cry.sh) - align the gene files for cryptochrome 4 and 5

[filter_alignments.sh](utilites/filter_alignments.sh) - runs 2-2_filter_alignments.py for all given alignment files and re-aligns them with mafft afterwards

[rename_taxa.sh](utilities/rename_taxa.sh) - calls rename_script.sh for all supplied .fasta-files

[rename_script.py](utilities/rename_script.py) - renames genes in supplied .fasta file for processing with AliGROOVE

[count_sequences.sh](utilities/count_sequences.sh) - counts all sequences within a folder of multiple sequence alignment files

[calculate_pairwise_time.sh](utilities/calculate_pairwise_time.sh) - calculates the time it takes to perform pairwise comparisons on sequences in provided files

[rename_trees.sh](utilities/rename_trees.sh) - calls 3_2_rename_trees.py to rename tips in generated gene trees to the corresponding IDX

[combine_trees.sh](utilities/combine_trees.sh) - uses ASTER to combine all given gene trees into consensus trees
