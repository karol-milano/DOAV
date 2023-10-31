#!/usr/bin/env Rscript

source("00_Utils.R")

lcVariabilidadesPorDesenvolvedor <- function() {
  path <- "../data/graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaCommits(file.names[i])
    gerarLCVariabilidadesPorDesenvolvedor(file.names[i], valores)
  }
}


#' Função que gera o gráfico LCVariabilidadesPorDesenvolvedorPeloTempo
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarLCVariabilidadesPorDesenvolvedor <- function(projeto, valores) {
  #projeto <- "gcc"
  #valores <- lerPlanilhaCommits(projeto)
  
  arq_var <- valores %>%
    select(Data, Classificacao, Variabilidades)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Classificacao", "Variabilidades")]), ]
  arq_var <- arq_var[!apply(arq_var, 1, function(x) any(x=="")), ]
  
  arq_var <- arq_var %>%
    group_by(Classificacao, Data) %>%
    summarise(Variabilities = n(), Valor = last(Data)) %>%
    arrange(Valor)
  
  arq_var[ , "Total"] = sum(arq_var[ , "Variabilities"])
  
  esp <- arq_var[arq_var$Classificacao == "Especialista", ]
  mis <- arq_var[arq_var$Classificacao == "Misto", ]
  
  tabela <- paste("../data/graphs/", projeto, "/18_", projeto, "_LCVariabitiesByClassification.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../data/graphs/", projeto, "/18_", projeto, "_LCVariabitiesByClassification.png", sep = "")
  
  png(file = imagem)
  
  plot(Lc(esp$Variabilities, n = arq_var$Total), col = "darkred", lwd = 2, cex = 1.5)
  lines(Lc(mis$Variabilities, n = arq_var$Total), col = "darkblue", lwd = 2, cex = 1.5)
  
  dev.off()
}
