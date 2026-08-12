#!/bin/bash

#SBATCH --partition rosa.p
#SBATCH --cpus-per-task=6
#SBATCH --mem=60G
#SBATCH --time=0-10:00
#SBATCH --output=/user/rego3475/master_output/logs/align_cry.%j.out
#SBATCH --error=/user/rego3475/master_output/logs/align_cry.%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=ronja.roesner@uol.de

### Documentation ###
# This is a utility script for the purpose of aligning all sequences in
# a number of given FASTA files for CRY

module load hpc-env/13.1
module load MAFFT/7.505-GCC-13.1.0-with-extensions
module load Python/3.11.3-GCCcore-13.1.0

startdate=$(date '+%Y_%m_%d-%H_%M_%S')
mkdir $WORK/wd-align_cry-$startdate
cd $WORK/wd-align_cry-$startdate

echo === start time is $(date '+%H:%M:%S') ===

mkdir aligned_fasta

file_list=$(ls ~/master_input/locus_CRY_full)

for file in $file_list; do
    cry_type=$(echo "${file##*_}" | cut -d'.' -f1)
    echo === aligning hits for $cry_type at $(date '+%H:%M:%S') ===
    # runs mafft on all combined hits for this exon
    mafft --thread 6 --auto ~/master_input/locus_CRY_full/$file > $cry_type-aligned.fasta
done

mv *-aligned.fasta ./aligned_fasta

echo === end time is $(date '+%H:%M:%S') ===
