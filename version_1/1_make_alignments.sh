#!/bin/bash

#SBATCH --partition rosa.p
#SBATCH --cpus-per-task=8
#SBATCH --mem=60G
#SBATCH --time=0-64:00
#SBATCH --output=/user/rego3475/master_output/logs/1_make_alignment.%j.out
#SBATCH --error=/user/rego3475/master_output/logs/1_make_alignment.%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=ronja.roesner@uol.de

### Documentation ###
# This is a master script for making multiple sequence alignments out of a set of
# genomes and genes. It calls on four other scripts.
# Inputs:
# - a genome dataset with the genomes named after their Accession Number.
# - a gene/exon dataset, current naming scheme is locus_Exxxx-NoDups_OK.fa
#	changing the naming scheme requires rewrite of code.
# - the utility subscript 'speciesinfo.py' requires an SQL database containing
#	information on the genomes in the dataset.


# get the starting time
startdate=$(date '+%Y_%m_%d-%H_%M_%S')
echo === start date and time is $startdate ===

# load necessary modules
module load hpc-env/13.1
module load parallel/20230822-GCCcore-13.1.0
module load HMMER/3.4-gompi-2023a
module load Python/3.11.3-GCCcore-13.1.0

# make working directory and move into it
mkdir $WORK/wd_make_al-$startdate
cd $WORK/wd_make_al-$startdate

# make output directories
mkdir hits hits-aligned hits-combined hits-renamed hmm nhmmer-tables trash
mkdir logs
mkdir logs/automatic

# make log files
touch logfile.log
touch genome_list.log

# when testing, use these, sets the amount of genomes and loci for checking
#genomecount=10
#locuscount=10

# when running with full dataset, use these - sets genomes and exons to all files in respective folders
genomecount=$(ls /nfs/data/zapp2497/genomes/raw_fasta/ | wc -l)
locuscount=$(ls ~/master_input/locus-fa_1105_nucleotide/ | wc -l)

# sets the amount of CPUs that nhmmer should use
cpu_count=8

# add the working directory and start time to the logfile
echo Working Directory: $(pwd) >> logfile.log
(echo  ;echo Starting at: $startdate) >> logfile.log

# declares a variable genomic_files containing the names all genomes in the dataset. Filter out any files listed in forbidden_genomes.txt
genomic_files=$(find /nfs/data/zapp2497/genomes/raw_fasta/ -type f -printf "%f\n" | grep -v -x -f ~/master_input/forbidden_genomes.txt | tail -n $genomecount)
echo ;echo genome files: $genomic_files;echo 

# declares a variable locus_files containing the names of all exons in the dataset
locus_files=$(ls ~/master_input/locus-fa_1105_nucleotide/ | head -n $locuscount)

echo === making hmm files at $(date '+%H:%M:%S') ===

# build .hmm files for all .al files in a subfolder of the working directory
for file in $locus_files; do 
	locus_id=$(echo "${file%%-*}")
	mkdir ./hits/$locus_id-allhits
	hmmbuild $file.hmm ~/master_input/locus-fa_1105_nucleotide/$file
done

# remove unnecessary clutter in file names by renaming all .hmm files
for f in *.fa.hmm; do mv -- "$f" "${f%.fa.hmm}.hmm"; done

# moves all .hmm files to their respective subdirectory
mv *.hmm ./hmm

echo === starting genomic analysis scripts at $(date '+%d.%m.%Y %H:%M:%S') ===
# prepares a function that runs the script for creating hit.fasta files for every genome
genomic_function() {
	genomic_in="$1"
	sbatch ~/genotree/1-1_process_genomes.sh $genomic_in $cpu_count
}

# exports the function so GNU Parallel can access it
export -f genomic_function

# runs genomic_script.sh in parallel for each specified genome
echo "$genomic_files" | parallel --eta --jobs $genomecount genomic_function

# waits for all genome files to be processed and nhmmer-tables to be created by checking the squeue command for a certain term
while squeue -u $USER | grep -q "1-1"; do wait; done

echo === starting locus analysis scripts at $(date '+%d.%m.%Y %H:%M:%S') ===
# prepares a function that runs the script for aligning all hits for each locus
align_function() {
	locus_in=$(echo "${1%%-*}")
	sbatch ~/genotree/1-3_align_loci.sh $locus_in $1
}

# exports the function so GNU Parallel can access it
export -f align_function

# runs align_tree_script.sh in parallel for each specified locus
echo "$locus_files" | parallel --eta --jobs $locuscount align_function

# waits for all trees to be created by checking the squeue command for a certain term
while squeue -u $USER | grep -q "1-3"; do wait; done

# add a list of all used genomes to the logfile
(echo  ;echo $genomecount genomes: ) >> logfile.log
for file in $genomic_files;do
	acc_number=$(echo "${file%%.fasta}")
	# add Accession Number to the genome list
	echo $acc_number >> genome_list.log
	# add genome information to the logfile
	(echo -n "$acc_number | ";echo -n $(python3 ~/genotree/utilities/speciesinfo.py -n "${file%%.fasta}" -d ~/master_input/genotree_master_library.db);echo ) >> logfile.log
done

# add a list of all loci to the logfile
(echo  ;echo $locuscount loci: )>> logfile.log
for file in $locus_files; do
	locus_id=$(echo "${file%%-NoDups_OK.fa}")
	(echo "$locus_id") >> logfile.log
done

enddate=$(date '+%Y_%m_%d-%H_%M_%S')

echo === moving files ===
# make folder for all outputs of this run
mkdir ~/master_output/raw_alignments/$enddate-all_out_FULL_DATASET_NEW

# add the ending time to the logfile and move all log files
(echo  ;echo Ending at: $enddate) >> logfile.log
mv logfile.log  logs/logfile_$enddate.log
mv genome_list.log logs/genomelist_$enddate.log

# move all output folders
mv * ~/master_output/raw_alignments/$enddate-all_out_FULL_DATASET_NEW

# remove the working directory
cd ~/genotree/
#rm -r $WORK/wd_make_al-$startdate

echo === end date and time is $enddate ===
