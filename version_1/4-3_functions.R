### Documentation ###
# helper script for providing several functions
# 
# Functions for external use:
# reroot_tree
# import_tree
# make_reference
# apply_annotation
# annotate_by_taxgroup
# get_bootstrap_plot
# make_comparison_subtree
# make_annotation_subtree
# trait_tree
# tangle_plots
# trait_tangle
# calculate_bootstrap
# 
# Helper functions for internal use:
# get_tips
# get_pure_block_nodes
# get_mrca
# fast_get_ancestral_state
# color_by_trait


# function for rerooting a phylotree object
reroot_tree <- function(phylotree, outgroup = "none")
{
  # if no outgroup is specified, return unrooted tree
  if (outgroup == "none")
  { 
    print("No outgroup supplied, returning unrooted tree...")
    return(phylotree)
  } else {
    # get the node for the outgroup for rerooting
    reroot_node <- ggtree::MRCA(phylotree, .node1 = outgroup)
    # reroot at specified node in the tree
    rerooted_tree <- ape::root(phylotree, reroot_node)
    print("Reroot successful, returning new tree...")
    return(rerooted_tree)
  }
}

# function for importing the specified tree and rerooting it
import_tree <- function(path, outgroup = "none")
{
  # import treefile
  tree <- read.tree(path)
  # if no outgroup is specified, return unrooted tree
  out_tree <- reroot_tree(tree,outgroup)
  return(out_tree)
}
import_dend <- function(path,outgroup = "none")
{
  dend <- read.dendrogram(path)
  out_dend <- dend
  return(out_dend)
}

# function for making a reference plot and saving it as a file
make_reference <- function(phylotree, savepath)
{
  renamed_reftree <- rename_taxa(phylotree, data_matrix, key = 1, value = mainTipName)
  reference_plot = ggtree(renamed_reftree, layout = "rectangular")
  reference_plot = reference_plot + theme_tree2() + geom_tiplab(offset=0.03) + geom_text(aes(label=node),hjust=-.3) + geom_rootpoint()
  # save generated tree as pdf
  ggsave(savepath,reference_plot,device="pdf",dpi=300,width=30,height=75,limitsize=FALSE)
}

# helper function that gets all descendant tips of a given node
# written with the help of GPT-o3 mini
get_tips <- function(tree, node) {
  clade <- extract.clade(tree, node)
  return(clade$tip.label)
}

# function to get the highest (maximal) pure clades for a given taxon group.
# written with the help of GPT-o3 mini
get_pure_block_nodes <- function(taxgroup, tree, taxgroup_type) {
  # get the taxa (e.g., species IDs) that should be in this taxonomic group.
  taxon_tips <- intersect(data_matrix$IDX[data_matrix[[taxgroup_type]] == taxgroup], tree$tip.label)
  n_tips <- length(tree$tip.label)
  pure_blocks <- c()
  
  # loop over all internal nodes
  for (node in (n_tips + 1):(n_tips + tree$Nnode)) {
    node_tips <- get_tips(tree, node)
    # check if the node is pure (all its descendant tips are from taxon_tips)
    if (all(node_tips %in% taxon_tips)) {
      # identify the parent node from the tree edge matrix.
      parent <- tree$edge[tree$edge[, 2] == node, 1]
      parent_is_pure <- FALSE
      if (length(parent) > 0) {
        parent_tips <- get_tips(tree, parent)
        if (all(parent_tips %in% taxon_tips)) {
          parent_is_pure <- TRUE
        }
      }
      # only record nodes that are not nested within a larger pure block.
      if (!parent_is_pure) {
        pure_blocks <- c(pure_blocks, node)
      }
    }
  }
  
  # return the set of maximal nodes that define pure blocks.
  return(pure_blocks)
}

# function that finds the MRCAs for a given taxgroup. Can detect paraphyletic groups
# written with the help of GPT-o3 mini
get_mrca <- function(taxgroup, tree, taxgroup_type) {
  # get the list of taxa IDs corresponding to the taxon group.
  taxon_tips <- intersect(data_matrix$IDX[data_matrix[[taxgroup_type]] == taxgroup], tree$tip.label)
  
  if (length(taxon_tips) > 1) {
    # if the whole group is monophyletic, we get one block.
    if (is.monophyletic(tree, taxon_tips)) {
      return(getMRCA(tree, tip = taxon_tips))
    } else {
      # for paraphyletic groups, return the maximal pure blocks.
      return(get_pure_block_nodes(taxgroup, tree, taxgroup_type))
    }
  } else if (length(taxon_tips) == 1) {
    # for a single tip, simply return that tip's node.
    return(MRCA(tree, .node1 = taxon_tips))
  } else {
    return("not in tree")
  }
}

# function for annotating the plot with colours
apply_annotation <- function(anno_plot, phylotree, lb, cl, fill = "none", cl_type="taxGroup")
{
  # search for most recent common ancestors of given taxon group
  node_vector <- get_mrca(lb, phylotree, cl_type)
  # if the taxon group is not in the tree, return unmodified plot
  if (node_vector[1] == "not in tree" || length(node_vector) == 0)
  {return(anno_plot)}
  
  # apply annotations for all clades in the tree
  for (nd in node_vector)
  {
    # set the label for the given clade
    anno_plot <- anno_plot + geom_cladelabel(node = nd, label = lb, color = cl, offset = .1,align = TRUE)
    
    # highlight nodes with specified parameters
    if (fill == "full")
    {anno_plot <- anno_plot + geom_hilight(node = nd,fill = cl,color = "black")}
    else if (fill == "rim")
    {anno_plot <- anno_plot + geom_hilight(node = nd, fill = "transparent", color = cl, linewidth = 0.75)}
    else if (fill == "none")
    {}
  }
  
  # return the modified plot
  return(anno_plot)
}

# function for annotating a ggtree phylo plot with colors and taxon group names
annotate_by_taxgroup <- function(taxgroup, phyloplot, phylotree, path="", fill="full", colorscheme="monochrome", col_vec=c(), include=c(), wd=30, ht=75, export=TRUE, output_format="pdf")
{
  tax_anno_plot <- phyloplot
  color_count <- length(unique(data_matrix[[taxgroup]]))
  # if the amount of colors given is equal to the amount of taxa
  if (length(col_vec)!=0 && length(col_vec)==color_count)
  { anno_colors <- col_vec }
  # if there are more taxa than colors given
  else if (length(col_vec)!=0 && length(col_vec)<color_count)
  {  
    col_diff <- color_count-length(col_vec)
    col_rand <- randomColor(count=col_diff,hue=colorscheme, luminosity = "dark")
    anno_colors <- c(col_vec,col_rand)
  }
  # if there are less taxa than colors given
  else if (length(col_vec)!=0 && length(col_vec)>color_count)
  { anno_colors <- col_vec[1:color_count] }
  # if no colors were given
  else
  { anno_colors <- randomColor(count=color_count, hue=colorscheme, luminosity = "dark") }
  
  print(paste("=== Generating tree for ",taxgroup," ===",sep = ""))
  index <- 1
  for (entry in unique(data_matrix[[taxgroup]])){
    print(paste(entry,anno_colors[index],sep=": "))
    
    if (length(include)==0)
    { tax_anno_plot <- apply_annotation(tax_anno_plot,phylotree,entry,anno_colors[index],fill=fill,cl_type=taxgroup) }
    else if (length(include)>0 && entry %in% include)
    { tax_anno_plot <- apply_annotation(tax_anno_plot,phylotree,entry,anno_colors[index],fill=fill,cl_type=taxgroup) }
    else
    { tax_anno_plot <- apply_annotation(tax_anno_plot,phylotree,entry,anno_colors[index],fill="none",cl_type=taxgroup) }
    index <- index+1
  }
  
  if (export==TRUE)
  {
    if (length(include)==0)
    { save_path <- paste0(path,taxgroup,".",output_format) }
    else
    { save_path <- paste0(path,taxgroup,"_only-",paste(include,collapse="-"),".",output_format)  }
    # save the created plot as a pdf
    ggsave(save_path,tax_anno_plot,device=output_format,width=wd,height=ht,limitsize=FALSE)
    print(paste("Colored tree saved as",save_path))
  }
  else
  { return(tax_anno_plot) }
  
}

# function for making a bootstrap phyloplot
get_bootstrap_plot <- function(phylotree,filter_value=0.95)
{
  # add phylotree with bootstrap values, by default shows values under 0.95
  bootstrap_tibble <- tibble(
    node=1:Nnode(phylotree)+Ntip(phylotree),
    bootstrap = ifelse(as.numeric(phylotree$node.label) > filter_value, "", phylotree$node.label))
  
  bootstrap_plot <- ggtree(phylotree, layout="rectangular") %<+% bootstrap_tibble
  bootstrap_plot <- bootstrap_plot + theme_tree2()+geom_rootpoint()+geom_text(aes(label=bootstrap),hjust=-0.1,size=3)+geom_tiplab(aes(label=label),offset=0.02)+theme_tree()
  
  return(bootstrap_plot)
}

make_comparison_subtree <- function(input_node,clade,phylotree,path,wd=10,ht=10,output_format="jpeg")
{
  print(paste0("=== Generating Comparison Subtree for ",clade," ==="))
  # create pdf device for saving
  save_path <- paste0(path,"Comp_",clade,".",output_format)
  # create device for saving
  if (output_format=="pdf")
    { pdf(file=save_path,width=wd,height=ht,units="in") }
  else if (output_format=="jpeg")
    { jpeg(file=save_path,width=wd,height=ht,units="in",res=300) }
  
  # get all descendants of input node
  tips <- c(getDescendants(phylotree,input_node))
  # get subtree of input node and title it
  subtree <- zoom(phylotree,tips,subtree = FALSE,align.tip.label=FALSE)
  
  # print the tree out
  print(subtree)
  dev.off()
  
  print(paste("Subtree tree saved as",save_path))
}

make_annotation_subtree <- function(input_node,clade,phylotree,path,anno_group="none",tree_layout="roundrect",reroot_node="none",node_labels=FALSE,anno_color="blue",wd=10,ht=10,export=TRUE,output_format="pdf")
{
  print(paste("=== Generating Annotated Subtree for ",clade," ===",sep=""))
  
  all_subtrees <- subtrees(phylotree)
  for (entry in all_subtrees) {
    if (entry$name==input_node){
      sub_tree <- entry
    }
  }
  if (!exists("sub_tree")){
    print("Node not found in tree.")
    exit
  } else {
    if (reroot_node!="none")
    { sub_tree <- reroot_tree(sub_tree,reroot_node) }
    
    renamed_subtree <- rename_taxa(sub_tree, data_matrix, key = 1, value = mainTipName)
    sub_plot <- ggtree(renamed_subtree,layout=tree_layout)
    if (node_labels==TRUE) {
    sub_plot <- sub_plot +
      theme_tree() +
      geom_rootpoint() +
      geom_tiplab(offset = 0.0005) +
      geom_text(aes(label=node),hjust=.1) +
      coord_cartesian(clip = "off") +
      hexpand(0.3) + 
      theme(plot.margin = margin(10, 10, 10, 10))
    } else {
      sub_plot <- sub_plot +
        theme_tree() +
        geom_rootpoint() +
        geom_tiplab(offset = 0.0005) +
        coord_cartesian(clip = "off") +
        hexpand(0.3) + 
        theme(plot.margin = margin(10, 10, 10, 10))
    }
  }
  save_path <- paste0(path,"Anno_",clade)
  if (anno_group!="none")
  {
    out_plot <- annotate_by_taxgroup(anno_group,sub_plot,sub_tree,path=save_path,colorscheme=anno_color,wd=wd,ht=ht,export=export,output_format=output_format)
  } else {
    out_plot <- sub_plot
    if (export==TRUE)
    {
      save_path <- paste0(save_path,".",output_format)
      ggsave(save_path,out_plot,device=output_format,width=wd,height=ht,limitsize=FALSE,units="in")
      print(paste0("Subtree saved as ",save_path))
    }
  }
  return_list <- list(
    subtree=renamed_subtree,
    subplot=out_plot)
  return(return_list)
}

# function for adding phylopic images to the tips of an existing phylo subtree
make_picture_subtree <- function(subtree, subgroup, save_path,save_mod, uuids=data.frame(name=character(), uid=character()), export=TRUE, tree_layout="roundrect")
{
  # rename tree tips to scientific names for image search
  subtree <- rename_taxa(subtree, data_matrix, key = mainTipName, value = ScientificName)
  # get the amount of tips for this tree
  tip_count <- length(subtree$tip.label)
  
  # perform uuid search if no or the wrong amount of uuids were given
  if (length(uuids$name)!=tip_count)
  {
    print(paste0("PhyloPic image search for ",tip_count, " species..."))
    # reset data frame to empty state
    uuids=data.frame(name=character(), uid=character())
    # get uuids for each species in the tree
    for (species in subtree$tip.label)
    {
      # get uuid for the current species, if it exists on phylopic
      uuid <- try(get_uuid(name = species),silent = TRUE)
      
      # if species is not on phylopic, search for genus
      if (inherits(uuid, "try-error"))
      { 
        print(paste0(species," not available on phylopic. Trying genus search."))
        genus <- unlist(strsplit(species," "))[1]
        uuid <- try(get_uuid(name = genus),silent = TRUE)
        # if genus is not on phylopic, skip species
        if (inherits(uuid, "try-error"))
        {
          print(paste0(genus, " not available on phylopic. Using generic image for subgroup (", subgroup, ")."))
          # add empty uuid to the dataframe
          uuid <- get_uuid(name = subgroup)
          uuids[nrow(uuids) + 1,] = c(species, uuid)
        }
        # add genusuid to the dataframe
        else
        { uuids[nrow(uuids) + 1,] = c(species, uuid) }
      }
      # add species uuid to the dataframe
      else
      { uuids[nrow(uuids) + 1,] = c(species, uuid) }
      
      # print the current species and uuid to the console
      print(paste0(species,": ",uuid))
    }
    print("PhyloPic search completed...")
  }
  
  print("Making Subtree Plot...")
  if (tip_count < 15)
  {
    print("Taxa count lower than 15, larger silhouette size")
    subplot <- ggtree(subtree, layout=tree_layout) %<+% uuids +
      geom_tiplab(aes(image=uid), size=0.2, geom="phylopic", offset=1, align = TRUE) +
      geom_tiplab(aes(label=label), offset = .05, vjust = -1) + xlim(NA, 2) +
      scale_color_viridis_c()
  } else {
    print("Taxa count higher than 15, smaller silhouette size")
    subplot <- ggtree(subtree, layout=tree_layout) %<+% uuids +
      geom_tiplab(aes(image=uid), size=0.02, geom="phylopic", offset=1, align = TRUE) +
      geom_tiplab(aes(label=label), offset = .05, vjust = -1) + xlim(NA, 2) +
      scale_color_viridis_c()
  }
  
  # export the plot if specified
  if (export==TRUE)
  { 
    out_path <- paste0(save_path,save_mod,"_SubtreePlot_Pictures_",subgroup,".png")
    # set the height of the plot to the nearest round 5 from the amount of taxa
    plot_height <- ceiling(tip_count / 5) * 5
    ggsave(out_path,subplot,device = "png", width = 10,height=plot_height) 
    print(paste0("Image saved to ", out_path))
  }
  # return the subplot
  return_list <- list(
    subplot = subplot,
    uuid_df = uuids
  )
  return(return_list)
}


# helper function to compute ancestral states in a bottom-up (postorder) pass.
# written with the help of GPT-4
fast_get_ancestral_state <- function(tree, tip_states) {
  Ntip <- length(tree$tip.label)
  Nnode <- tree$Nnode
  total_nodes <- Ntip + Nnode
  # preallocate a vector for all node states; initializing with NA.
  states <- rep(NA, total_nodes)
  
  # fill in states for the tip nodes.
  # ensure tip_states is named with tip labels.
  states[1:Ntip] <- tip_states[tree$tip.label]
  
  # process internal nodes in numerical order (internal nodes are often > Ntip).
  # assuming that for a rooted tree, for every internal node the children have lower numbers.
  for (node in (Ntip + 1):total_nodes) {
    # get children nodes for this internal node from the edge matrix.
    children <- tree$edge[tree$edge[, 1] == node, 2]
    child_states <- states[children]
    # if any child has an NA state or the children disagree, mark as NA.
    if (any(is.na(child_states)) || length(unique(child_states)) > 1) {
      states[node] <- NA
    } else {
      states[node] <- unique(child_states)
    }
  }
  return(states)
}

# function for recursively coloring each branch
# of a phylotree by the state of a given binary trait
# written with the help of GPT-4
color_by_trait <- function(col_plot, char_col_name, cl) {
  # assume that rerooted_tree is your tree and tree_data is a tibble version obtained earlier.
  Ntip <- length(rerooted_tree$tip.label)
  
  # extract the trait states for the tips from tree_data.
  # this assumes that tree_data is ordered such that the first Ntip rows correspond to tips.
  tip_states <- tree_data[[char_col_name]][1:Ntip]
  # name the tip states with corresponding tip labels.
  names(tip_states) <- rerooted_tree$tip.label
  # compute ancestral states for all nodes using the fast bottom-up approach.
  ancestral_states <- fast_get_ancestral_state(rerooted_tree, tip_states)
  # add the ancestral state information to tree_data.
  tree_data$char_in <- ancestral_states
  
  # build the plot using ggtree, mapping the computed states onto branches and tips.
  col_plot <- col_plot %<+% tree_data +
    geom_tree(aes(shape = factor(char_in), color = factor(char_in))) +
    geom_tippoint(aes(color = factor(char_in)), size = 3) +
    scale_color_manual(
      values = c("0" = "black", "1" = cl, "NA" = "gray"),
      labels = c("not present", "present", "unknown")
    ) +
    labs(color = char_col_name, shape = char_col_name) +
    theme(
      legend.position = "top",
      legend.title.position = "left",
      legend.justification = c("left", "top"),
      legend.title = element_text(size = 25),
      legend.text = element_text(size = 20),
      legend.background = element_rect(linewidth = 0.35, color = "grey"),
      legend.margin = margin(6, 6, 6, 6),
      legend.box = "vertical"
    )
  
  return(col_plot)
}

# function for generating a tree that has the specified trait mapped onto it
trait_tree <- function(save_path, treeplot, trait, color)
{
  print(paste("=== Generating Trait Tree for ",trait," colored in ",color," ===",sep=""))
  main_plot_trait <- color_by_trait(treeplot, trait, color)
  
  ggsave(save_path,main_plot_trait,device="pdf",width=35,height=75,limitsize=FALSE)
  print(paste("Trait tree saved as",save_path))
}

# function for constructing tanglegrams for the two supertrees
tangle_plots <- function(tree_left, tree_right, out_dir,savemod1,savemod2,treename_a="",treename_b="",main_name="",rotate_nodes=TRUE)
{
  # prune all leaves that are not in both trees
  if (length(tree_left$tip.label)!=length(tree_right$tip.label))
  {
    # get vector containing common tips of both trees
    common_tips <- intersect(tree_left$tip.label, tree_right$tip.label)
    # prune leaves that are not in both trees
    tree_left <- keep.tip(tree_left, common_tips)
    tree_right <- keep.tip(tree_right, common_tips)
    # remove duplicate leaves
    tree_left$tip.label <- make.unique(tree_left$tip.label)
    tree_right$tip.label <- make.unique(tree_right$tip.label)
  }
  
  # pre-rotate the tree tips for better matching
  if (rotate_nodes==TRUE)
  {
    rotated_trees <- tangler::pre.rotate(tree_left,tree_right)
    tree_left <- rotated_trees[[1]]
    tree_right <- rotated_trees[[2]]
  }
  
  # make dendrograms from the phylo trees
  dend_left <- as.dendrogram.phylo(tree_left)
  dend_right <- as.dendrogram.phylo(tree_right)
  
  # make unmodified tangle plot
  print(paste0("Making Tanglegram for ",treename_a," and ",treename_b,"..."))
  tangle <- tanglegram(dend1 = dend_left, dend2 = dend_right)
  # set path for saving file
  savepath <- paste0(out_dir,savemod1,"-Tanglegram_Compare-",savemod2,".pdf")
  print(paste0("Plotting Tanglegram for ",treename_a," and ",treename_b,"..."))
  # open pdf device for saving
  pdf(savepath,width=40,height=45)
  # modify tangle plot and save it
  plot(tangle,
       main_left = treename_a, main_right = treename_b,
       main = main_name,
       highlight_branches_col = TRUE,
       margin_top = 10,
       columns_width = c(6,4,6),
       sort = FALSE)
  dev.off()
  print(paste0("Tanglegram for ",treename_a," and ",treename_b," saved as\n",savepath))
}


# make secondary tangle plot with trait annotation
# can map a boolean trait onto the connection lines (possible values: 0, 1, NA)
trait_tangle <- function(data_matrix, trait_name, tree_left, tree_right, outgroup, threshold, savemod, rotate_nodes=TRUE)
{
  
  print("getting trait data")
  # get trait data for all possible genomes
  
  trait_data <- setNames(
    data.frame(data_matrix$mainTipName, data_matrix[[trait_name]]),
    c("tip.label", trait_name)
  )
  
  # get vector containing common tips of both trees
  common_tips <- intersect(tree_left$tip.label, tree_right$tip.label)
  
  # prune all leaves that are not in both trees
  if (length(tree_left$tip.label)!=length(tree_right$tip.label))
  {
    print("pruning tree and trait data")
    # remove trait data for tips not in both trees
    trait_data <- trait_data[trait_data$tip.label %in% common_tips, ]
    # prune leaves that are not in both trees
    tree_left <- keep.tip(tree_left, common_tips)
    tree_right <- keep.tip(tree_right, common_tips)
    # remove duplicate leaves
    tree_left$tip.label <- make.unique(tree_left$tip.label)
    tree_right$tip.label <- make.unique(tree_right$tip.label)
  }
  
  print("preparing metadata")
  # prepare metadata with dynamic trait column name
  meta <- data.frame(
    tip.label = c(common_tips, setdiff(c(tree_left$tip.label, tree_right$tip.label), common_tips)),
    group = rep(c("A","B"), length.out = Ntip(tree_left) + Ntip(tree_right))
  )
  meta <- merge(meta,trait_data,by="tip.label",all_x=TRUE)
  meta <- meta %>%
    mutate(
      !!sym(trait_name) := factor(  # Dynamic column name
        .data[[trait_name]],  # Safe column access
        levels = c(0, 1),
        labels = c("no", "yes")
      )
    )
  # add color column using case_when
  meta <- meta %>%
    mutate(
      trait_color = case_when(
        is.na(meta[[trait_name]]) ~ "grey",
        meta[[trait_name]] == "yes" ~ "green1",
        meta[[trait_name]] == "no" ~ "blue"
      )
    )
  
  print(table(meta$trait_color,useNA="always"))
  
  print(anti_join(meta, data.frame(label = tree_left$tip.label), by = c("tip.label" = "label")))
  
  print(all(meta$trait_color %in% colors()))
  
  # pre-rotate nodes for better matching
  if (rotate_nodes==TRUE)
  {
    rotated_trees <- tangler::pre.rotate(tree_left,tree_right)
    tree_left <- rotated_trees[[1]]
    tree_right <- rotated_trees[[2]]
    savemod <- paste0("rotated_",savemod)
  }
  
  print("plotting trees")
  # create ggtree objects
  gg_left <- ggtree(tree_left) %<+% meta + 
    geom_tiplab() + 
    # color tip points. still broken, only colors in grey
    geom_tippoint(aes(color=as.factor(trait_color)))
  gg_right <- ggtree(tree_right) %<+% meta + 
    geom_tiplab()
  
  # set colors for line annotation
  sampletypecolors <- c("no" = "blue", "yes" = "green1")
  # make tanglegram
  tangle_common <- common.tanglegram(
    gg_left,
    gg_right,
    trait_name,
    sampletypecolors,
    tiplab = TRUE,
    t2_tiplab_size = 3,
    lab_pad = 0.5
  )
  # display tanglegram
  plot(tangle_common)
  # save the generated plot as a pdf file
  save_path <- paste0(out_dir,"r",outgroup,"-",threshold,"-Tanglegram_Trait-",trait_name,"-",savemod,".pdf")
  ggsave(
    save_path,
    tangle_common,
    device = "pdf",
    width = 40,
    height = 45,
    limitsize = FALSE
  )
  print(paste0("Tangle plot saved as ",save_path))
  return(tangle_common)
}

# function for calculating the mean bootstrap value of a phylo tree
calculate_bootstrap <- function(phylotree, savemod, return_values=FALSE)
{
  # extract bootstrap values
  bs_values <- phylotree$node.label
  # turn bootstrap values numeric
  numeric_bs <- as.numeric(bs_values)
  # remove NA values if they exist
  numeric_bs <- numeric_bs[!is.na(numeric_bs)]
  # calculate mean bootstrap value
  mean_bs <- mean(numeric_bs)
  # calculate median bootstrap value
  median_bs <- median(numeric_bs)
  # if the bootstrap is given as 0.xy, turn it into percentage
  if (mean_bs<=1)
  { mean_bs <- mean_bs*100 }
  # if the bootstrap is given as 0.xy, turn it into percentage
  if (median_bs<=1)
  { median_bs <- median_bs*100 }
  # print mean value and return it if specified
  print(paste0("Values for ",savemod,": "))
  print(paste0("Mean bootstrap value: ", round(mean_bs, digits=2),"%"))
  print(paste0("Median bootstrap value: ", round(median_bs, digits=2),"%"))
  if (return_values==TRUE)
  { 
    return_list <- list(
      mean_bootstrap=mean_bs,
      median_bootstrap=median_bs
    )
    return(return_list) 
  }
}