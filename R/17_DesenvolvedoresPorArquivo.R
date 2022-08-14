#!/usr/bin/env Rscript

source("00_Utils.R")

desenvolvedoresPorArquivo <- function() {
  path <- "../graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaAutores(file.names[i])
    gerarDesenvolvedoresPorArquivo(file.names[i], valores)
  }
}

gerarDesenvolvedoresPorArquivo <- function(projeto, valores) {
  #projeto <- "Gawk"
  #valores <- lerPlanilhaAutores(projeto)
  
  arq_var <- valores %>%
    select(Arquivo, Desenvolvedor)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Arquivo", "Desenvolvedor")]), ]
  
  arq_var <- arq_var %>%
    group_by(Arquivo) %>%
    summarise(Desenvolvedor = n())

  tabela <- paste("../graphs/", projeto, "/17_", projeto, "_DevelopersByFile.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../graphs/", projeto, "/17_", projeto, "_DevelopersByFile.png", sep = "")
  
  png(file = imagem)
  
  p <- arq_var %>%
    ggplot(aes(x = "", y = Desenvolvedor)) +
    geom_violin(fill="lightskyblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
    geom_boxplot(width=0.1, fill="lightskyblue1") +
    stat_summary(fun.data = n_fun, geom = "text", color = "red", size = 12) +
    theme(plot.title = element_text(size=22)) +
    labs(x = "Files", y = "Amount of Developers",
         title = "Developers by Files")
  
  print(p)
  
  dev.off()
}
