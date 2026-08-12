### Documentation ###
# utility script for calculating the time it will take
# to perform a pairwise comparison of all sequences in
# the specified files. User can specify the time per comparison.
#
# usage sh calculate_pairwise_time.sh <time_per_comparison> <file_format> </path/to/files>


time_per_comp=${1:-0.3}
file_format=${2:-".fasta"}
file_path=${3:-$(pwd)}

file_list=$(ls $file_path/*$file_format)

echo
echo === Info on pairwise comparisons for $file_format in $file_path ===
for file in $file_list; do
    file_name=$(echo "${file##*/}")
    sequence_count=$(grep -c "^>" "$file")
    comparison_count=$(echo $(( $sequence_count * ($sequence_count - 1) / 2 )))
    comparison_time=$(echo "scale=2; $comparison_count * $time_per_comp / 60" | bc -l)
    comparison_hours_minutes=$(echo $comparison_time | awk '{h=int($1/60); m=$1%60; printf "%dh %dm\n", h, m + (m-int(m)>=0.5)}')
    
    echo $file_name: $sequence_count Sequences, amounts to $comparison_count pairwise comparisons.
    echo "Approximate time until completion: $comparison_time minutes ($comparison_hours_minutes)."
    echo 
    
done