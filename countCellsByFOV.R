count_cells_by_FOV <- function(rdaFile){
  oo=readRDS(rdaFile)
  oo$geom.data %>% count(Sample,FOV)
}
