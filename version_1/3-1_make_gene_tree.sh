#!/bin/bash

#SBATCH --partition rosa.p
#SBATCH --cpus-per-task=8
#SBATCH --mem=60G
#SBATCH --time=0-16:00
#SBATCH --output=./logs/3-1_make_gene_tree.%j.out
#SBATCH --error=./logs/3-1_make_gene_tree.%j.err
#SBATCH --mail-type=FAIL
#SBATCH --mail-user=ronja.roesner@uol.de

### Documentation ###
# Helper script for making individual gene trees from a given
# multiple sequence alignment using IQ-TREE 2


# load necessary modules
module load hpc-env/13.1
module load Python/3.11.3-GCCcore-13.1.0
module load IQ-TREE/2.2.2.7-gompi-2023a

alignment_file=${1}

# creates a tree for this aligned hitfile
iqtree2 -s $alignment_file -T 8 --tbe --alrt 10000    

# renames tree branches to simplify analysis
python3 ~/genotree/3-2_rename_trees.py -t $alignment_file.treefile -d ~/master_input/genotree_master_library.db