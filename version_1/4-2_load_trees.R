### Documentation ###
# helper script for providing a function to load the supertrees into the workspace

# function for loading the supertree into the workspace
load_supertree <- function(outgroup, threshold, aster_ver, tree_layout){
  # set import tree and modificator for saving pdfs
  treefile <- paste0("data/treefiles-",threshold,"/consensus-",threshold,"-",aster_ver,".treefile")
  savemod <- paste0("r", outgroup, "-",threshold,"-",aster_ver,"-",tree_layout)
  out_dir <- paste0("output/",savemod,"/")
  
  # make output subdirectory if it doesn't exist
  if (!file.exists(out_dir))
  { dir.create(out_dir) }
  
  # open the connection to the log file
  log_file <- file(paste(out_dir,savemod,"_README.log",sep=""),open="wt",blocking=FALSE)
  
  # use custom function to get data from the SQL database
  sql_data <- load_matrix(outgroup)
  data_matrix <-sql_data$data_matrix
  outgroup_name <- sql_data$outgroup_name
  
  headline <- glue("Rooted on {outgroup_name} (IDX {outgroup}).\nThreshold value {threshold}, ASTER version of original consensus tree was {aster_ver}.")
  writeLines(headline,con=log_file,sep="\n")
  # close the connection to the log file
  close(log_file)
  
  # set tip names for all output trees
  data_matrix$refTipName <- paste("(",data_matrix$IDX,")",sep="")
  data_matrix$mainTipName <- paste(data_matrix$ScientificName," (",data_matrix$IDX,")",sep="")
  
  # import the specified treefile and reroot it at the specified outgroup
  rerooted_tree <- import_tree(treefile, outgroup)
  
  # rename taxa in rerooted tree
  renamed_tree <- rename_taxa(rerooted_tree, data_matrix, key = 1, value = mainTipName)
  
  # make tree visualization basic plot and set aesthetic parameters
  base_plot <- ggtree(renamed_tree,layout = tree_layout)
  if (tree_layout=="rectangular" || tree_layout=="roundrect") {
    base_plot <- base_plot+theme_tree2()+geom_rootpoint()+geom_tiplab(offset=0)+theme_tree()
  } else if (tree_layout=="circular") {
    base_plot <- base_plot+theme_tree2()+geom_rootpoint()+geom_tiplab(offset=0.5)+geom_treescale()+theme_tree()
  }
  
  bootstrap_plot <- get_bootstrap_plot(renamed_tree)
  
  return_list <- list(
    treefile=treefile,
    savemod=savemod,
    out_dir=out_dir,
    data_matrix=data_matrix,
    rerooted_tree=rerooted_tree,
    renamed_tree=renamed_tree,
    base_plot=base_plot,
    bootstrap_plot=bootstrap_plot
  )
  
  return(return_list)
}

# function for loading the CRY gene trees into the workspace
load_CRY_tree <- function(outgroup, cry_type, threshold, tree_layout)
{
  # set import tree and modificator for saving pdfs
  treefile <- paste0("data/treefiles-CRY-",threshold,"/",cry_type,"-",threshold,"-renamed",".treefile")
  savemod <- paste0("r", outgroup,"-",cry_type,"-",threshold,"-",tree_layout)
  out_dir <- paste0("output/",savemod,"/")
  
  # make output subdirectory if it doesn't exist
  if (!file.exists(out_dir))
  { dir.create(out_dir) }
  
  # use custom function to get data from the SQL database
  sql_data <- load_matrix(outgroup)
  data_matrix <-sql_data$data_matrix
  
  # set tip names for all output trees
  data_matrix$refTipName <- paste("(",data_matrix$IDX,")",sep="")
  data_matrix$mainTipName <- paste(data_matrix$ScientificName," (",data_matrix$IDX,")",sep="")
  
  # import the specified treefile and reroot it at the specified outgroup
  rerooted_tree <- import_tree(treefile, outgroup)
  
  # rename taxa in rerooted tree
  renamed_tree <- rename_taxa(rerooted_tree, data_matrix, key = IDX, value = mainTipName)
  
  # make tree visualization basic plot and set aesthetic parameters
  base_plot <- ggtree(renamed_tree,layout = tree_layout)
  if (tree_layout=="rectangular" || tree_layout=="roundrect") {
    base_plot <- base_plot+theme_tree2()+geom_rootpoint()+geom_tiplab(offset=0)+theme_tree()
  } else if (tree_layout=="circular") {
    base_plot <- base_plot+theme_tree2()+geom_rootpoint()+geom_tiplab(offset=0.5)+geom_treescale()+theme_tree()
  }
  
  bootstrap_plot <- get_bootstrap_plot(renamed_tree, filter_value = 95)
  
  return_list <- list(
    treefile=treefile,
    savemod=savemod,
    out_dir=out_dir,
    data_matrix=data_matrix,
    rerooted_tree=rerooted_tree,
    renamed_tree=renamed_tree,
    base_plot=base_plot,
    bootstrap_plot=bootstrap_plot
  )
  
  return(return_list)
}

# function for loading data from the SQL database
load_matrix <- function(outgroup)
{
  # import data matrix from SQLite database
  db_conn <- dbConnect(RSQLite::SQLite(), "data/genotree_master_library_corrected.db")
  matrix_query <- "SELECT ids.IDX, ids.AccessionNumber, taxonomy.ScientificName, taxonomy.Authority, taxonomy.Phylum, taxonomy.Gigaclass, taxonomy.Class, taxonomy.taxOrder, taxonomy.Family, taxonomy.Genus, taxonomy.taxGroup, traits.isMarine, traits.isBrackish, traits.isFresh, traits.isAllWater, traits.isMarineFresh, traits.isTerrestrial, traits.isMigratory
  FROM ids 
  INNER JOIN taxonomy 
  ON ids.IDX = taxonomy.IDX
  INNER JOIN traits
  ON ids.IDX = traits.IDX"
  data_matrix <- dbGetQuery(db_conn, matrix_query)
  outgroup_name <- dbGetQuery(db_conn, glue_sql(.con=db_conn,"SELECT ScientificName FROM taxonomy WHERE IDX={outgroup}"))$ScientificName
  dbDisconnect(db_conn)
  # rename taxOrder column from SQLite database to Order in dataframe
  colnames(data_matrix)[which(names(data_matrix) == "taxOrder")] <- "Order"
  
  return(list(data_matrix=data_matrix, outgroup_name=outgroup_name))
}


