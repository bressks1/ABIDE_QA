library(dplyr)
ABIDE = read.csv("ABIDE_QA_results_070523.csv")
ABIDE$site = gsub("_.*$","",ABIDE$MR.ID)
ABIDE = ABIDE[ABIDE$Included == 1,]

sub = ABIDE %>% group_by(site) %>% slice_sample(., prop = .3)
sub = sub[,-1]
write.csv(sub, "QA_visualinspection.csv", row.names = F)
