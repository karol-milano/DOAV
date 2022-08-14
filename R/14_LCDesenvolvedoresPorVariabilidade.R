#!/usr/bin/env Rscript

source("00_Utils.R")

lcDesenvolvedoresPorVariabilidade <- function() {
  path <- "../data/graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaCommits(file.names[i])
    gerarLCDesenvolvedoresPorVariabilidade(file.names[i], valores)
  }
}


#' Função que gera o gráfico LCDesenvolvedoresPorVariabilidadePeloTempo
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarLCDesenvolvedoresPorVariabilidade <- function(projeto, valores) {
  #projeto <- "Hexchat"
  #valores <- lerPlanilhaCommits(projeto)
  
  arq_var <- valores %>%
    select(Data, Desenvolvedor, Variabilidades)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Desenvolvedor", "Variabilidades")]), ]
  arq_var <- arq_var[!apply(arq_var, 1, function(x) any(x=="")), ]
  
  arq_var <- arq_var %>%
    group_by(Variabilidades) %>%
    summarise(Developers = n(), Valor = last(Data)) %>%
    arrange(Valor)
  
  arq_var[ , "Total"] = sum(arq_var[ , "Developers"])
  
  tabela <- paste("../data/graphs/", projeto, "/14_", projeto, "_LCDevelopersByVariability.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../data/graphs/", projeto, "/14_", projeto, "_LCDevelopersByVariability.png", sep = "")
  
  png(file = imagem)
  
  plot(Lc(arq_var$Developers, n = arq_var$Total), col = "darkred", lwd = 2, cex = 1.5)
  
  dev.off()
}
