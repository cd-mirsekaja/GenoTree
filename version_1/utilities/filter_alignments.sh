#!/bin/bash

#SBATCH --partition rosa.p
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G
#SBATCH --time=0-4:00
#SBATCH --output=/user/rego3475/master_output/logs/utility-filter_alignments.%j.out
#SBATCH --error=/user/rego3475/master_output/logs/utility-filter_alignments.%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=ronja.roesner@uol.de

### Documentation ###
# utility for filtering all multiple sequence alignments
# in a given folder for the given threshold
# 
# usage sbatch filter_alignments.sh <threshold>


threshold=${1:-0.35}

# load necessary modules
module load hpc-env/13.1
module load parallel/20230822-GCCcore-13.1.0
module load Python/3.11.3-GCCcore-13.1.0
module load MAFFT/7.505-GCC-13.1.0-with-extensions


startdate=$(date '+%Y_%m_%d-%H_%M_%S')
mkdir /dss/work/rego3475/wd_filter-realign_CRY_$startdate_$threshold
cd /dss/work/rego3475/wd_filter-realign_CRY_$startdate_$threshold

mkdir filtered_fasta filtered_realigned_fasta filter_tables

#alignment_path=$(~/master_input/all_hits_aligned_renamed)
alignment_path=~/master_input/locus_CRY_full/aligned_files
aligroove_path=~/master_input/AliGROOVE_Matrices/CRY_Matrices

echo === Filtering alignments with threshold $threshold ===

aligroove_files=$(find $aligroove_path/*matrix.txt -type f -printf "%f\n" | grep -v -x -f ~/master_input/forbidden_loci.txt)
aligroove_count=$(echo $aligroove_files | wc -w)

filter_function(){
    aligroove_matrix=${1}
    # get ID for current locus
    locus_id=$(echo "${aligroove_matrix##*/}" | cut -d'-' -f1)

    echo Locus ID: $locus_id
    alignment_file=$alignment_path/$locus_id-aligned.fasta

    # filters alignments for current locus for all exons with a score under the given threshold
    python3 ~/genotree/2-2_filter_alignments.py -d $aligroove_path/$aligroove_matrix -a $alignment_file -l $locus_id -t $threshold
}

# export the function so it can be used in the script
export -f filter_function

# filter every alignment file in the list
for aligroove_matrix in $aligroove_files; do
    filter_function $aligroove_matrix
done

# move filtered alignments and value tables to subfolder
mv *-filtered.fasta filtered_fasta
mv *-values.csv filter_tables

# set variable with a list of all filtered fasta files
filtered_files=$(ls filtered_fasta/*-filtered.fasta)

# re-align every filtered fasta file
for file in $filtered_files; do
    locus_id=$(echo "${file##*/}" | cut -d'-' -f1)
    echo re-aligning $locus_id
    mafft --thread 8 --auto $file > $locus_id-filtered-realigned.fasta
done

# move re-aligned fasta files to subdirectory
mv *-filtered-realigned.fasta filtered_realigned_fasta

cd ~/genotree
#rm -r /dss/work/rego3475/wd_filter-realign_$startdate_$threshold