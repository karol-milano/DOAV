#!/usr/bin/env Rscript

source("00_Utils.R")

variabilidadesPorCommit <- function() {
  path <- "../data/graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaCommits(file.names[i])
    gerarVariabilidadesPorCommit(file.names[i], valores)
  }
}


#' Função que gera o gráfico VariabilidadesPorCommit
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarVariabilidadesPorCommit <- function(projeto, valores) {
  #projeto <- "Collected"
  #valores <- lerPlanilhaCommits(projeto)
  
  arq_var <- valores %>%
    select(Commit, Variabilidades)

  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Commit", "Variabilidades")]), ]
  arq_var <- arq_var[!apply(arq_var, 1, function(x) any(x=="")), ]
  
  arq_var <- arq_var %>%
    group_by(Commit) %>%
    summarise(Variabilidades = n())
  
  tabela <- paste("../data/graphs/", projeto, "/03_", projeto, "_VariabilitiesPerCommit.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../data/graphs/", projeto, "/03_", projeto, "_VariabilitiesPerCommit.png", sep = "")
  
  png(file = imagem)
  
  p <- arq_var %>%
    ggplot(aes(x = "", y = Variabilidades)) + 
    geom_violin(fill="lightskyblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
    geom_boxplot(width=0.1, fill="lightskyblue1") +
    stat_summary(fun.data = n_fun, geom = "text", color = "red", size = 12) +
    theme(legend.position = "none") +
    labs(x = "Commits", y = "Amount of Variabilities",
         title = "Variabilities per commit"
    )
  
  print(p)
  
  dev.off()
  
}
