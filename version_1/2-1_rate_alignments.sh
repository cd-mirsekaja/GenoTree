#!/bin/bash

#SBATCH --partition rosa.p
#SBATCH --cpus-per-task=10
#SBATCH --mem=80G
#SBATCH --time=0-20:00
#SBATCH --output=./logs/2-1_rate_alignments.%j.out
#SBATCH --error=./logs/2-1_rate_alignments.%j.err
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=ronja.roesner@uol.de

### Documentation ###
# Helper script for scoring an input multiple sequence alignment
# using AliGROOVE


# load necessary modules
module load hpc-env/13.1
source ~/.bashrc

locus_id="$1"
input_path="$2"

echo === starting scoring for locus $locus_id at $(date '+%H:%M:%S') ===
~/programs/Aligroove/AliGROOVE_v.1.08.pl -i ~/master_input/locus_CRY_full/aligned_files/$locus_id-aligned.fasta
