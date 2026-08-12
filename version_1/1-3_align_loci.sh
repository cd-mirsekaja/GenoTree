#!/bin/bash

#SBATCH --partition rosa.p
#SBATCH --cpus-per-task=6
#SBATCH --mem=60G
#SBATCH --time=0-16:00
#SBATCH --output=./logs/automatic/1-3_align_loci.%j.out
#SBATCH --error=./logs/automatic/1-3_align_loci.%j.err
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=ronja.roesner@uol.de

### Documentation ###
# This is a helper script for the purpose of aligning all sequences in
# a given FASTA file. This file is made from all hit files for the input
# locus.
# Gets a locusID as input with the naming scheme 'Locus_Exxxx'


module load hpc-env/13.1
module load MAFFT/7.505-GCC-13.1.0-with-extensions
module load Python/3.11.3-GCCcore-13.1.0

locus_id="$1"

# display start time in log file
echo === start time for $locus_id is $(date '+%H:%M:%S') ===

# combines all created .fasta files for this locus into one file
cat hits/$locus_id-allhits/* >> $locus_id-combined_hits.fasta

# zip the original hit files for this locus and remove the empty folder
zip $locus_id-allhits.zip hits/$locus_id-allhits/* -m
mv $locus_id-allhits.zip ./hits
rm -r ./hits/$locus_id-allhits


echo === aligning hits for $locus_id ===
# runs mafft on all combined hits for this exon
mafft --thread 6 --auto $locus_id-combined_hits.fasta > $locus_id-aligned.fasta

echo === renaming file for further processing ===
python3 ~/genotree/utilities/rename_script.py -f $locus_id-aligned.fasta -d ./hits-renamed

echo === moving files ===
# move all combined, tree and miscellaneous files to their respective subfolders
mv $locus_id-aligned.fasta ./hits-aligned
mv $locus_id-combined_hits.fasta ./hits-combined

# display end time in log file
echo === end time for $locus_id is $(date '+%H:%M:%S') ===