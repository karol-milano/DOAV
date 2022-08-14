#!/usr/bin/env Rscript

source("00_Utils.R")

variabilidadesPorArquivo <- function() {
  path <- "../data/graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaAutores(file.names[i])
    gerarVariabilidadesPorArquivo(file.names[i], valores)
  }
}


#' Função que gera o gráfico VariabilidadesPorArquivo
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarVariabilidadesPorArquivo <- function(projeto, valores) {
  #projeto <- "Cherokee"
  #valores <- lerPlanilhaAutores(projeto)
  
  arq_var <- valores %>%
    select(Arquivo, Variabilidades)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Arquivo", "Variabilidades")]), ]
  arq_var <- arq_var[!apply(arq_var, 1, function(x) any(x=="")), ]
  
  arq_var <- arq_var %>%
    group_by(Arquivo) %>%
    summarise(Variabilidades = n())
  
  tabela <- paste("../data/graphs/", projeto, "/01_", projeto, "_VariabilitiesPerFile.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../data/graphs/", projeto, "/01_", projeto, "_VariabilitiesPerFile.png", sep = "")
  
  png(file = imagem)
  
  p <- arq_var %>%
    ggplot(aes(x = "", y = Variabilidades)) + 
    geom_violin(fill="lightskyblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
    geom_boxplot(width = 0.1, fill = "lightskyblue1") +
    stat_summary(fun.data = n_fun, geom = "text", color = "red", size = 12) +
    theme(legend.position = "none") +
    labs(x = "Arquivo", y = "Amount of Variabilities",
         title = "Variabilities per file")
  
  print(p)
  
  dev.off()
}
