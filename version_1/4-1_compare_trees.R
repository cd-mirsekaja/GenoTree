#!/usr/bin/env Rscript

### Documentation ###
# Master script for making Tanglegrams from multiple phylogenetic
# trees.
# 
# Input:
# - several phylogenetic trees in NEWICK format
# 
# Output:
# - Tanglegrams of the input trees in PDF format


# remove all variables from environment
rm(list=ls())

# load required libraries
library(ape)
library(tidyverse)
library(ggtree)
library(treeio)
library(DBI) # SQLite-Library
library(glue)
library(randomcoloR)
library(dendextend)
library(phylogram)
library(tangler)
# import custom functions
source("/Users/privatstudium/Documents/Programming/Bachelorarbeit/0_genotree_repository/4-2_load_trees.R")
source("/Users/privatstudium/Documents/Programming/Bachelorarbeit/0_genotree_repository/4-3_functions.R")


# set working directory
setwd("~/Documents/Programming/Bachelorarbeit/tree_recoloring/main")

# set outgroup for rerooting. 298 is Petromyzon marinus, 359 is Asterias rubens, 362 is Pecten maximus
outgroup <- "359"
# set threshold modifier
threshold_1 <- "thr0_35"
threshold_2 <- "thr0_35-realigned"
# set layout for export tree. Can be 'rectangular', 'roundrect', 'circular'.
tree_layout <- "rectangular"
# set aster version modifier
aster_ver_1 <- "astralpro3"
aster_ver_2 <- "astral4"
# set cryptochrome version
cry_type <- "CRY5"
# set save modifier
savemod <- paste0("r", outgroup, "-",threshold_1)
# set output directory and make it if neccessary
out_dir <- paste0("output/",threshold_1,"-tanglegrams/")
if (!file.exists(out_dir))
{ dir.create(out_dir) }

# use custom function to import tree objects
tree_ap3_data <- load_supertree(outgroup,threshold_1,aster_ver_1,tree_layout)
tree_ap3_real_data <- load_supertree(outgroup,threshold_2,aster_ver_1,tree_layout)
tree_a4_data <- load_supertree(outgroup,threshold_1,aster_ver_2,tree_layout)
tree_a4_real_data <- load_supertree(outgroup,threshold_2,aster_ver_2,tree_layout)
# import cryptochrome trees
tree_cry_data <- load_CRY_tree(outgroup,cry_type,threshold_1,tree_layout)

data_matrix <- tree_a4_real_data$data_matrix

# get the supertrees trees from imported data
tree_ap3 <- tree_ap3_data$renamed_tree
tree_ap3_real <- tree_ap3_real_data$renamed_tree
tree_a4 <- tree_a4_data$renamed_tree
tree_a4_real <- tree_a4_real_data$renamed_tree
# get the cryptochrome trees from imported data
tree_cry <- tree_cry_data$renamed_tree


# tangle plot for ASTRAL-Pro3 and ASTRAL-4
tangle_plots(tree_ap3,tree_a4,out_dir,savemod,
             "AP3-A4",
             "ASTRAL-Pro3","ASTRAL-IV")
# tangle plot for ASTRAL-Pro3 and re-aligned ASTRAL-Pro3
tangle_plots(tree_ap3,tree_ap3_real,out_dir,savemod,
             "AP3-AP3_realigned",
             "ASTRAL-Pro3","ASTRAL-Pro3 (re-aligned)")
# tangle plot for ASTRAL-4 and re-aligned ASTRAL-4
tangle_plots(tree_a4,tree_a4_real,out_dir,savemod,
             "A4-A4_realigned",
             "ASTRAL-IV","ASTRAL-IV (re-aligned)")
# tangle plot for re-aligned ASTRAL-Pro3 and re-aligned ASTRAL-4
tangle_plots(tree_ap3_real,tree_a4_real,out_dir,savemod,
             "AP3_realigned-A4_realigned",
             "ASTRAL-Pro3 (re-aligned)","ASTRAL-IV (re-aligned)",
             "Tanglegram of the two main supertrees, made from re-aligned FASTA")

# tangle plot for re-aligned ASTRAL-IV and CRY trees
tangle_plots(tree_a4_real_pruned,tree_cry_pruned,out_dir,savemod,
             "A4_realigned-CRY5",
             "ASTRAL-IV (re-aligned)","Cryptochrome 5",
             "Tanglegram of the supertree and a gene tree")

# alternative tangle plot with the migratory trait highlighted
trait_tangle(data_matrix,"isMigratory",
             tree_a4_real,tree_cry,
             outgroup,threshold_1,"A4_realigned-CRY5",
             rotate_nodes = TRUE)


trait_tangle(data_matrix, "isMarine",
             tree_ap3_real,tree_a4_real,
             outgroup,threshold_1,"A4_realigned-AP3_realigned",
             rotate_nodes = TRUE)

#col_rand <- randomcoloR::distinctColorPalette(k=40)

#unbranch_dend_ap3 <- unbranch(dend_ap3,k=length(col_rand))
#clus = dendextend::cutree(unbranch_dend_ap3, length(col_rand))
#plot(as.phylo(dend_ap3), type = "phylogram", tip.color = col_rand[clus],
#     label.offset = 0, cex = 0.7)
