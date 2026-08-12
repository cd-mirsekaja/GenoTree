### Documentation ###
# utility that calls part of the pipeline to rename tree tips
# 
# usage sh rename_trees.sh <path/to/treefiles> <save_modifier>

tree_dir=${1}
savemod=${2}

cd /dss/work/rego3475/wd_test

startdate=$(date '+%Y_%m_%d-%H_%M_%S')
mkdir trees-renamed_$startdate

tree_files=$(ls $tree_dir)

for tree_file in $tree_files; do
    locus_id=$(echo "${tree_file##*/}" | cut -d'-' -f1)
    python3 ~/genotree/3-2_rename_trees.py -t $tree_dir/$tree_file -d ~/master_input/genotree_master_library.db -l $locus_id
done

mv *-renamed.treefile trees-renamed_$startdate

