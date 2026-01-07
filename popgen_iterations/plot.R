library("tidyverse")
library("scico")

the_data <- read.table(file="summary_popgen_iterations.csv",sep=";",header=T)
ggplot(data = the_data,
       mapping = aes(x = l1_init, y = l2_init_i)) +
    geom_tile(mapping = aes(fill = l1)) +
    facet_grid(~m) +
    scale_fill_scico(palette="bam")
#    scale_fill_gradient2(
#        low = "blue",
#        mid = "white",
#        high = "red",
#        midpoint = 0.5
#    )