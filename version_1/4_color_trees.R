#!/usr/bin/env Rscript

### Documentation ###
# Master script for generating annotated phylogenetic trees
# and exporting them in pdf or jpeg formats
# Input:
# - a phylogenetic tree (.treefile) in NEWICK format
# 
# Output:
# - several pdf and jpeg files with different annotated trees


# remove all variables from environment
rm(list=ls())
# load required libraries
library(data.tree)
library(ape)
library(tidyverse)
library(ggtree)
library(treeio)
library(phytools)
library(geiger)
library(randomcoloR)
library(rphylopic)
library(DBI) # SQLite-Library
library(glue) # for making nice text
library(svglite) # for exporting trees as svg for manual annotation
# import custom functions
source("/Users/privatstudium/Documents/Programming/Bachelorarbeit/0_genotree_repository/4-3_functions.R")

# set working directory
setwd("~/Documents/Programming/Bachelorarbeit/tree_recoloring/main")

# set outgroup for rerooting. 298 is Petromyzon marinus, 359 is Asterias rubens, 362 is Pecten maximus
outgroup <- "359"
# set threshold modifier
threshold <- "thr0_35"
threshold_CRY <- "thr0_35"
# set type of tree
tree_type <- "SUPERTREE"
# set aster version modifier
aster_ver <- "astral4"
# OR set cryptochrome version
cry_type <- "CRY5"
# set layout for export tree. Can be 'rectangular', 'roundrect', 'circular'.
tree_layout <- "rectangular"

# get functions for loading tree objects
source("/Users/privatstudium/Documents/Programming/Bachelorarbeit/0_genotree_repository/4-2_load_trees.R")

#EITHER load supertree and plot objects into workspace
if (tree_type=="SUPERTREE")
{
  
  supertree_data <- load_supertree(outgroup,threshold,aster_ver,tree_layout)
  savemod <- supertree_data$savemod
  data_matrix <- supertree_data$data_matrix
  out_dir <- supertree_data$out_dir
  rerooted_tree <- supertree_data$rerooted_tree
  renamed_tree <- supertree_data$renamed_tree
  base_plot <- supertree_data$base_plot
  bootstrap_plot <- supertree_data$bootstrap_plot
# OR load gene tree for a set cryptochrome type
} else if (tree_type=="CRY")
{
  
  cry_tree_data <- load_CRY_tree(outgroup,cry_type,threshold_CRY,tree_layout)
  savemod <- cry_tree_data$savemod
  data_matrix <- cry_tree_data$data_matrix
  out_dir <- cry_tree_data$out_dir
  rerooted_tree <- cry_tree_data$rerooted_tree
  renamed_tree <- cry_tree_data$renamed_tree
  base_plot <- cry_tree_data$base_plot
  bootstrap_plot <- cry_tree_data$bootstrap_plot
}

# get mean bootstrap value
calculate_bootstrap(renamed_tree,savemod,return_values = FALSE)

# set output paths for saved files
path_colored <- paste0(out_dir,savemod,"_ColoredPlot_")
path_bootstrap <- paste0(out_dir,savemod,"_BootstrapPlot_")
path_subtree <- paste0(out_dir,savemod,"_SubtreePlot_")

# set vectors with annotation colors
anno_colors_class <- c("green3","blue","brown","purple4","blue","violet","green2","grey","blue","black","blue","green4","pink4","red4")
anno_colors_taxgroup <- c("green3","blue","brown","purple4","violet","green2","grey","black","green4","pink4","red4","grey","darkgrey")


# make reference plot without renamed tips
make_reference(rerooted_tree, paste(out_dir, savemod, "_ReferencePlot.pdf", sep = ""))

### Annotated Trees ###

# make tree annotated with class
annotate_by_taxgroup("Class",base_plot,rerooted_tree,path_colored,col_vec = anno_colors_class,fill="full")
annotate_by_taxgroup("Class",base_plot,rerooted_tree,path_colored,col_vec = anno_colors_class, include = c("Teleostei","Holostei","Chondrostei","Cladistii","Elasmobranchii"))

# make tree annotated with taxGroup
annotate_by_taxgroup("taxGroup", base_plot,rerooted_tree, path_colored, col_vec = anno_colors_taxgroup)
annotate_by_taxgroup("taxGroup", base_plot,rerooted_tree, path_colored, col_vec = anno_colors_taxgroup, include=c("Fish"))

# make assorted annotated trees
annotate_by_taxgroup("Phylum",base_plot,rerooted_tree,path_colored,colorscheme = "blue")
annotate_by_taxgroup("Order",base_plot,rerooted_tree,path_colored,colorscheme = "blue")
annotate_by_taxgroup("Family", base_plot,rerooted_tree,path_colored,colorscheme = "blue")

# save uncolored tree as pdf
ggsave(paste(out_dir,savemod,"_MainPlot.pdf", sep=""),base_plot,device="pdf",width=35,height=75,limitsize=FALSE)

# save uncolored bootstrap tree as pdf
ggsave(paste0(out_dir,savemod,"_BootstrapPlot.pdf"),bootstrap_plot,device="pdf",width=35,height=75,limitsize=FALSE)

# make annotated bootstrap trees
annotate_by_taxgroup("Class",bootstrap_plot,rerooted_tree,path_bootstrap,col_vec = anno_colors_class,output_format="pdf")
annotate_by_taxgroup("Order",bootstrap_plot,rerooted_tree,path_bootstrap,colorscheme = "blue")


### Subtrees ###
# check ASTER version and make subtrees
if (tree_type=="SUPERTREE" && aster_ver=="astral4")
{
  # block for ASTRAL-IV
  # with the main tree on the left
  make_comparison_subtree(407,"Birds",renamed_tree,path_subtree,10,10)
  make_comparison_subtree(405,"Sauropsida",renamed_tree,path_subtree,10,15)
  make_comparison_subtree(405,"Mammals",renamed_tree,path_subtree,10,10)
  make_comparison_subtree(400,"Fish",renamed_tree,path_subtree,20,50)
  
  # without the main tree on the left, annotated by order
  make_annotation_subtree(405,"Sauropsida",rerooted_tree,path_subtree,anno_group="Order",export=TRUE,output_format="jpeg",wd=25,ht=15)
  make_annotation_subtree(400,"Fish",rerooted_tree,path_subtree,anno_group="Order",export=TRUE,output_format="jpeg",wd=35,ht=50,reroot_node=8)
  
  make_annotation_subtree(557,"Salmoniformes",rerooted_tree,path_subtree,output_format="jpeg",export=TRUE,wd=15,ht=5)
  make_annotation_subtree(513,"Anguilliformes",rerooted_tree,path_subtree,output_format="jpeg",export=TRUE,wd=15,ht=5)
  
  anguilliformes <- make_annotation_subtree(513,"Anguilliformes",rerooted_tree,path_subtree,export=FALSE)
  salmoniformes <- make_annotation_subtree(557,"Salmoniformes",rerooted_tree,path_subtree,export=FALSE)
  birds <- make_annotation_subtree(407,"Aves",rerooted_tree,path_subtree,export=FALSE)
  mammals <- make_annotation_subtree(405,"Mammalia",rerooted_tree,path_subtree,export=FALSE)
  falco <- make_annotation_subtree(466,"Falco",rerooted_tree,path_subtree,export=FALSE)
  
  make_picture_subtree(anguilliformes$subtree,"Anguilliformes",out_dir,savemod,export=TRUE)
  make_picture_subtree(salmoniformes$subtree,"Salmoniformes",out_dir,savemod,export=TRUE)
  make_picture_subtree(birds$subtree,"Aves",out_dir,savemod,export=TRUE)
  make_picture_subtree(mammals$subtree,"Mammalia",out_dir,savemod,export=TRUE)
  make_picture_subtree(falco$subtree,"Falco",out_dir,savemod,export=TRUE)
    
} else if (tree_type=="SUPERTREE" && aster_ver=="astral-pro3") {
  # block for ASTRAL-Pro3
  # with the main tree on the left
  make_comparison_subtree(419,"Birds",renamed_tree,path_subtree,10,10)
  make_comparison_subtree(417,"Sauropsida",renamed_tree,path_subtree,10,15)
  make_comparison_subtree(507,"Amphibians",renamed_tree,path_subtree,10,10)
  make_comparison_subtree(469,"Mammals",renamed_tree,path_subtree,10,10)
  make_comparison_subtree(412,"Fish",renamed_tree,path_subtree,20,50)
  make_comparison_subtree(569,"Salmoniformes",renamed_tree,path_subtree,10,5)
  make_comparison_subtree(527,"Anguilliformes",renamed_tree,path_subtree,10,5)
  
  # without the main tree on the left, annotated by order
  make_annotation_subtree(417,"Sauropsida",rerooted_tree,path_subtree,anno_group="Order",output_format="jpeg",export=TRUE,wd=25,ht=15)
  # subtree for the fish, rooted at Petromyzon marinus
  make_annotation_subtree(412,"Fish",rerooted_tree,path_subtree,anno_group="Order",output_format="jpeg",export=TRUE,wd=35,ht=50,reroot_node=21)
  
  make_annotation_subtree(569,"Salmoniformes",rerooted_tree,path_subtree,output_format="jpeg",export=TRUE,wd=15,ht=5)
  make_annotation_subtree(527,"Anguilliformes",rerooted_tree,path_subtree,output_format="jpeg",export=TRUE,wd=15,ht=5)
  
  # check cryptochrome version and make subtrees
} else if (tree_type=="CRY" && cry_type=="CRY5")
{
  # Block for CRY5
  # without the main tree on the left, annotated by order
  make_annotation_subtree(583,"Sauropsida",rerooted_tree,path_subtree,anno_group="Order",export=TRUE,output_format="jpeg",wd=25,ht=15)
  make_annotation_subtree(581,"Fish",rerooted_tree,path_subtree,anno_group="Order",export=TRUE,output_format="jpeg",wd=35,ht=50,reroot_node=8)
  
  make_annotation_subtree(524,"Salmoniformes",rerooted_tree,path_subtree,output_format="jpeg",export=TRUE,wd=15,ht=5)
  
  salmoniformes <- make_annotation_subtree(524,"Salmoniformes",rerooted_tree,path_subtree,export=FALSE)
  make_picture_subtree(salmoniformes$subtree,"Salmoniformes",out_dir,savemod,export=TRUE)
  
} else if (tree_type=="CRY" && cry_type=="CRY4")
{
  make_annotation_subtree(142,"Salmoniformes_Group1",rerooted_tree,path_subtree,output_format="jpeg",export=TRUE,wd=15,ht=5)
  make_annotation_subtree(156,"Salmoniformes_Group2",rerooted_tree,path_subtree,output_format="jpeg",export=TRUE,wd=15,ht=5)
  
  salmoniformes_1 <- make_annotation_subtree(142,"Salmoniformes_Group1",rerooted_tree,path_subtree,export=FALSE)
  salmoniformes_2 <- make_annotation_subtree(156,"Salmoniformes_Group2",rerooted_tree,path_subtree,export=FALSE)
  make_picture_subtree(salmoniformes_1$subtree,"Salmoniformes_Group1",out_dir,savemod,export=TRUE)
  make_picture_subtree(salmoniformes_2$subtree,"Salmoniformes_Group2",out_dir,savemod,export=TRUE)
  
} else if (tree_type=="CRY" && cry_type=="CRY_DASH")
{
  make_annotation_subtree(538,"Salmoniformes",rerooted_tree,path_subtree,output_format="jpeg",export=TRUE,wd=15,ht=5)
  
  salmoniformes <- make_annotation_subtree(538,"Salmoniformes",rerooted_tree,path_subtree,export=FALSE)
  make_picture_subtree(salmoniformes$subtree,"Salmoniformes",out_dir,savemod,export=TRUE)
}



### Trait-Trees ###
# make a ggtree phylo plot for annotating with the traits
main_plot_traits <- annotate_by_taxgroup("Order",base_plot,rerooted_tree,fill="none",export=FALSE)

# convert Index column in data_matrix to character (ChatGPT)
data_matrix$IDX <- as.character(data_matrix$IDX)
# convert tree to a tibble for easier manipulation (ChatGPT)
tree_data <- as_tibble(rerooted_tree)
# join the data matrix with the tree data based on the tip labels (ChatGPT)
tree_data <- tree_data %>%
  left_join(data_matrix, by = c("label" = "IDX"))

# map traits onto its own tree and save the trees as pdfs
trait_tree(paste(out_dir,savemod,"_TraitPlot_Migration.pdf",sep=''),main_plot_traits,"isMigratory","orange")
trait_tree(paste(out_dir,savemod,"_TraitPlot_Marine.pdf",sep=''),main_plot_traits,"isMarine","blue")
trait_tree(paste(out_dir,savemod,"_TraitPlot_Fresh.pdf",sep=''),main_plot_traits,"isFresh","lightblue")
trait_tree(paste(out_dir,savemod,"_TraitPlot_Brackish.pdf",sep=''),main_plot_traits,"isBrackish","purple")
trait_tree(paste(out_dir,savemod,"_TraitPlot_AllWater.pdf",sep=''),main_plot_traits,"isAllWater","blue")
trait_tree(paste(out_dir,savemod,"_TraitPlot_Terrestrial.pdf",sep=''),main_plot_traits,"isTerrestrial","orange")


