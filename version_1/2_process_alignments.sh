#!/bin/bash

#SBATCH --partition rosa.p
#SBATCH --cpus-per-task=8
#SBATCH --mem=60G
#SBATCH --time=0-24:00
#SBATCH --output=/user/rego3475/master_output/logs/2_process_alignments.%j.out
#SBATCH --error=/user/rego3475/master_output/logs/2_process_alignments.%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=ronja.roesner@uol.de

### Documentation ###
# This is a master script for processing multiple sequence alignments.
# It calls on three other scripts.
# Input:
# - a folder containing a number of multiple sequence alignments, the name must end on *.fasta
# 
# Output:
# - a folder containing FASTA files that were filtered, then re-aligned.


# get the starting time and set an attachment for folder names
attachment="CRY_full"
startdate=$(date '+%Y_%m_%d-%H_%M_%S')
echo === start date and time is $startdate ===

# load necessary modules
module load hpc-env/13.1
module load parallel/20230822-GCCcore-13.1.0
module load Python/3.11.3-GCCcore-13.1.0

# make working directory and move into it
mkdir $WORK/wd-al_scoring-$startdate-$attachment
cd $WORK/wd-al_scoring-$startdate-$attachment

# make output directories
mkdir logs aligroove_output alignments_filtered filter_tables alignments_filtered_realigned
mkdir aligroove_output/txt aligroove_output/svg 

# get a low amount of files, use for testing
#alignment_count=5

# get only allowed files, use for filtered dataset
#alignment_count=$(cat master_input/allowed_loci.txt | wc -w)

# set path for input files
#alignment_path=~/master_input/all_hits_aligned_renamed
alignment_path=~/master_input/locus_CRY_full/aligned_files
alignment_modifier=aligned

# get all files, use for full dataset
alignment_count=$(ls $alignment_path/*.fasta | wc -l)

# save all relevant alignment files with only allowed loci in a variable
#alignment_files=$(find $alignment_path/*.fasta -type f -printf "%f\n" | grep -f ~/master_input/allowed_loci.txt | head -n $alignment_count)

# save all relevant alignment files in a variable
alignment_files=$(ls $alignment_path/*.fasta | head -n $alignment_count)

echo == used $alignment_count alignment files: $alignment_files ==
find $alignment_path/*.fasta -type f -printf "%f\n" | grep -f ~/master_input/allowed_loci.txt | head -n $alignment_count

echo === starting alignment scoring at $(date '+%d.%m.%Y %H:%M:%S') ===
# prepares a function that runs the script for scoring each alignment
scoring_function() {
	locus_in=$(echo "${1##*/}" | cut -d'-' -f1)
	sbatch ~/genotree/2-1_rate_alignments.sh $locus_in $alignment_path
}

# exports the function so GNU Parallel can access it
export -f scoring_function

# runs 2-1_rate_alignments.sh in parallel for each specified exon
echo "$alignment_files" | parallel --eta --jobs $alignment_count scoring_function

# waits for all alignments to be rated by checking the squeue command for a certain term
while squeue -u $USER | grep -q "2-1_rate"; do wait; done

echo === finished alignment scoring at $(date '+%d.%m.%Y %H:%M:%S') ===

mv $alignment_path/*.txt ./aligroove_output/txt
mv $alignment_path/*.svg ./aligroove_output/svg

echo === calculating total mean and median scores ===
printf "locusID;scoreMedian;scoreMean\n" > total_scores.csv

# calculate total mean and median scores for all alignments
for file in ./aligroove_output/txt/*.txt; do
    locus_id=$(echo "${file##*/}" | cut -d'_' -f5 | cut -d'-' -f1)
    echo - $locus_id -
    python3 ~/genotree/utilities/total_score.py -f $file -l $locus_id
done

# move score table to output folder
mv total_scores.csv ./aligroove_output

# set filter threshold
threshold=0.35
echo === filtering alignments for score threshold $threshold ===
for file in $alignment_files; do
    # get ID for current locus
    locus_id=$(echo "${file##*/}" | cut -d'-' -f1)
    aligroove_matrix=./aligroove_output/txt/AliGROOVE_seqsim_matrix_$locus_id-$alignment_modifier.txt
    echo filtering locus ID: $locus_id
    # filters alignments for current locus for all exons with a score under the given threshold
    python3 ~/genotree/2-2_filter_alignments.py -d $aligroove_matrix -a $file -l $locus_id -t $threshold
done

# move filtered alignments and filter tables to output folder
echo === moving files ===
mv *-filtered.fasta ./alignments_filtered
mv *-values.csv ./filter_tables

filtered_files=$(ls alignments_filtered/*-filtered.fasta)

for file in $filtered_files; do
    locus_id=$(echo "${file##*/}" | cut -d'-' -f1)
    echo re-aligning $locus_id
    mafft --thread 6 --auto $file > $locus_id-filtered-realigned.fasta
done

mv *-filtered-realigned.fasta alignments_filtered_realigned


# get the end time and move all files to the output folder
enddate=$(date '+%Y_%m_%d-%H_%M_%S')
mkdir ~/master_output/filtered_alignments/$enddate-alignments_$attachment
mv * ~/master_output/filtered_alignments/$enddate-alignments_$attachment

# remove the working directory
cd ~/genotree
#rm -r $WORK/wd-al_scoring-$startdate-$attachment
