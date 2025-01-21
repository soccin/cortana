read_cell_segmentation<-function(sfile) {
    read_csv(sfile,col_names=c("X","Y","CellNum"))
}

compute_cell_stats<-function(xi) {

    area=nrow(xi)
    wholeCells=unique(xi$CellNum[!is.na(xi$CellNum)])
    nuclei=unique(xi$NucNum[!is.na(xi$NucNum)])

    cn=xi %>% count(NucNum) %>% arrange(desc(n)) %>% mutate(pct=n/sum(n)) %>% slice(1) %>% as.list
    cw=xi %>% count(CellNum) %>% arrange(desc(n)) %>% mutate(pct=n/sum(n)) %>% slice(1) %>% as.list

    tibble(
        Xcenter=sum(xi$X)/area,
        Ycenter=sum(xi$Y)/area,
        Area=area,
        NumWholeCells=len(wholeCells),
        WholeCells=paste0(sort(wholeCells),collapse=";"),
        NumNuclei=len(nuclei),
        Nuclei=paste0(sort(nuclei),collapse=";"),
        DomCell=cw$CellNum,
        DomCellPct=cw$pct,
        DomNuc=cn$NucNum,
        DomNucPct=cn$pct
    )

}

require(tidyverse)

require(furrr)
if(Sys.getenv("LSB_DJOB_NUMPROC")=="") {
    CORES=8
} else {
    CORES=as.numeric(Sys.getenv("LSB_DJOB_NUMPROC"))
}
cat("Cores =",CORES,"\n")
#options(future.globals.maxSize=1000*1024^2)
plan(multisession,workers=CORES)

argv=commandArgs(trailing=T)

nucFile=argv[1]
#nucFile="mesmer-output/GBM_049/R005/both/GBM_049_R005_nuc_seg.csv"
wcFile=gsub("_nuc_seg","_wc_seg",nucFile)

sampleFOV=basename(nucFile) %>% gsub("_nuc_.*","",.)
sampleId=gsub("_R[0-9]*","",sampleFOV)
FOV=gsub(".*_R","",sampleFOV)

sn=read_cell_segmentation(nucFile) %>% rename(NucNum=CellNum)
sw=read_cell_segmentation(wcFile)

ss=full_join(sn,sw)

tblN=ss %>% split(.$NucNum) %>% future_map(compute_cell_stats,.progress=T) %>% bind_rows(.id="ObjectId") %>% mutate(Sample=sampleId,FOV=FOV) %>% select(Sample,FOV,ObjectId,everything())
dn=tblN %>% arrange(desc(NumWholeCells)) %>% head(20) %>% pull(Nuclei)
#tblN %>% arrange(desc(NumWholeCells)) %>% filter(Nuclei %in% dn)

tblC=ss %>% split(.$CellNum) %>% future_map(compute_cell_stats,.progress=T) %>% bind_rows(.id="ObjectId") %>% mutate(Sample=sampleId,FOV=FOV) %>% select(Sample,FOV,ObjectId,everything())

tblC=tblC %>% select(-matches("DomCell|WholeCells")) %>% rename(WholeCellId=ObjectId)
tblN=tblN %>%
    select(-matches("DomNuc|Nuclei")) %>%
    rename(NucleusId=ObjectId) %>%
    mutate(WholeCellId=ifelse(DomCellPct>=.8,DomCell,NA))

odir=dirname(nucFile) %>% gsub("both","tables",.)
fs::dir_create(odir)

write_csv(tblN,file.path(odir,cc("objectTbl_Nucleus_",sampleId,"",FOV,".csv.gz")))
write_csv(tblC,file.path(odir,cc("objectTbl_WholeCell_",sampleId,"",FOV,".csv.gz")))


multiNuc=tblN %>% filter(!is.na(WholeCellId)) %>% count(WholeCellId) %>% filter(n>1) %>% arrange(desc(n)) %>% head(12) %>% pull(WholeCellId)

pmn=sw %>%
    filter(CellNum %in% multiNuc) %>%
    group_by(CellNum) %>%
    left_join(sn) %>%
    mutate(fNuc=as.numeric(factor(NucNum))%>%factor) %>%
    ggplot(aes(X,Y,color=fNuc)) + theme_light() +
        ggrastr::rasterise(geom_point(size=sqrt(3),alpha=.6)) +
        facet_wrap(~CellNum,ncol=4,scale="free") + ggsci::scale_color_nejm(na.value="grey75") + ggtitle(paste(sampleId,FOV))

# pltFile=file.path(odir,cc("multiNucCells_",sampleId,"",FOV,".png"))
# png(filename=pltFile,type="cairo",units="in",width=11,height=8.5,pointsize=12,res=300)
# print(pmn)
# dev.off()

pltFile=file.path(odir,cc("multiNucCells_",sampleId,"",FOV,".pdf"))
pdf(file=pltFile,width=11,height=8.5)
print(pmn)
dev.off()
