#!/usr/bin/env Rscript

source("00_Utils.R")

variabiliadadesPorDesenvolvedorPeloTempo <- function() {
  path <- "../data/graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaCommits(file.names[i])
    gerarVariabilidadesPorDesenvolvedorPeloTempo(file.names[i], valores)
  }
}


#' Função que gera o gráfico VariabilidadesPorDesenvolvedorPeloTempo
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarVariabilidadesPorDesenvolvedorPeloTempo <- function(projeto, valores) {
  #projeto <- "Marlin"
  #valores <- lerPlanilhaCommits(projeto)
  
  arq_var <- valores %>%
    select(Desenvolvedor, Data, Variabilidades, EhAutor)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Desenvolvedor", "Data", "Variabilidades")]), ]
  
  arq_var <- arq_var %>%
    group_by(Desenvolvedor, Data, EhAutor) %>%
    summarise(Variabilidades = n())
  
  arq_var['EhAutor'][arq_var['EhAutor'] == "Autor"] <- "Author"
  arq_var['EhAutor'][arq_var['EhAutor'] == "Colaborador"] <- "Collaborator"
  
  tabela <- paste("../data/graphs/", projeto, "/09_", projeto, "_VariabilitiesPerDeveloperOverTime.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../data/graphs/", projeto, "/09_", projeto, "_VariabilitiesPerDeveloperOverTime.png", sep = "")
  
  png(file = imagem)
  
  p <- arq_var %>%
    ggplot(aes(x = EhAutor, y = Variabilidades, fill = EhAutor)) + 
    geom_violin(fill="lightskyblue", draw_quantiles = c(0.25, 0.5, 0.75)) + 
    geom_boxplot(width=0.1, fill="lightskyblue1") +
    stat_summary(fun.data = n_fun, geom = "text", color = "red", size = 12) +
    theme(legend.position = "none") +
    labs(x = "", y = "Amount of Variabilities",
         title = "Variabilities per Developer")
  
  print(p)
  
  dev.off()
}
