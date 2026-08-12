#!/usr/bin/env bash
# this script was written with the help of GPT o3-mini
### Documentation ###
# utility to calculate the total, mean and median amounts of gene sequences in a folder of .fasta multiple sequence alignments.
# gets the directory for the unfiltered and filtered files as a parameter.
# 
# usage bash count_sequences.sh <path/to/unfiltered/files> <path/to/filtered/files>

compute_stats() {
    # All files are passed as parameters
    local files=("$@")
    local counts=() total=0
    if [ "${#files[@]}" -eq 0 ]; then
        echo "No FASTA files found."
        return 1
    fi

    # Loop over each file and count lines starting with '>'
    for file in "${files[@]}"; do
        # Using grep -c with a regex for sequences (FASTA headers start with '>')
        count=$(grep -c "^>" "$file")
        counts+=("$count")
        total=$(( total + count ))
    done

    # Calculate mean. Using awk to allow floating point division.
    local n=${#counts[@]}
    local mean
    mean=$(awk -v tot="$total" -v n="$n" 'BEGIN { printf "%.2f", tot/n }')

    # Sort counts to calculate median.
    IFS=$'\n' sorted=($(sort -n <<<"${counts[*]}"))
    unset IFS

    local median
    if (( n % 2 == 1 )); then
        # For an odd number of elements, pick the middle value.
        median="${sorted[$((n/2))]}"
    else
        # For an even number, median is the average of the two central values.
        lower="${sorted[$((n/2-1))]}"
        upper="${sorted[$((n/2))]}"
        median=$(awk -v l="$lower" -v u="$upper" 'BEGIN { printf "%.2f", (l + u) / 2 }')
    fi

    echo "$total $mean $median"
}

# set input files, filtered files are passed to the script as an argument
unfiltered_dir=${1}
unfiltered_files=("$unfiltered_dir"/*.fasta)
filtered_dir=${2}
filtered_files=("$filtered_dir"/*.fasta)

# calculate mean, median and total sequence counts
read unfiltered_total unfiltered_mean unfiltered_median < <(compute_stats "${unfiltered_files[@]}")
read filtered_total filtered_mean filtered_median < <(compute_stats "${filtered_files[@]}")

# calculate differences between the values
total_diff=$(( unfiltered_total - filtered_total ))
mean_diff=$(awk -v u="$unfiltered_mean" -v f="$filtered_mean" 'BEGIN { printf "%.2f", u - f }')
median_diff=$(awk -v u="$unfiltered_median" -v f="$filtered_median" 'BEGIN { printf "%.2f", u - f }')

# display calculated values
echo "Unfiltered FASTA files statistics:"
echo " Total sequences: $unfiltered_total"
echo " Mean count: $unfiltered_mean"
echo " Median count: $unfiltered_median"
echo ""
echo "Filtered FASTA files statistics:"
echo " Total sequences: $filtered_total"
echo " Mean count: $filtered_mean"
echo " Median count: $filtered_median"
echo ""

# display differences between calculated values
echo "Differences (unfiltered - filtered):"
echo " Total difference: $total_diff"
echo " Mean difference: $mean_diff"
echo " Median difference: $median_diff"