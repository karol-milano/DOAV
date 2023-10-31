#!/usr/bin/env Rscript

source("00_Utils.R")

tabelaGini <- function() {  
  x <- data.frame()
  path <- "../data/graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaCommits(file.names[i])
    x <- rbind(x, gerarTabelaGini(file.names[i], valores))
  }
  
  mean_row <- c("Mean", mean(x[,2]), mean(x[,3]))
  x <- rbind(x, mean_row)
  
  write.table(x, file="../data/graphs/19_TabelaGiniClassificacao.csv", sep=",", row.names=F)
}


#' Função que gera a tabela TabelaGini
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarTabelaGini <- function(projeto, valores) {
  #projeto <- "Marlin"
  #valores <- lerPlanilhaCommits(projeto)
  
  ##############################################################################
  ##### Commits por Desenvolvedor
  ##############################################################################
  
  arq_var <- valores %>%
    select(Data, Classificacao, Variabilidades)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Classificacao", "Variabilidades")]), ]
  
  arq_var <- arq_var %>%
    group_by(Classificacao, Data) %>%
    summarise(Variabilities = n(), Valor = last(Data)) %>%
    arrange(Valor)
  
  arq_var[ , "Cumulativo"] = cumsum(arq_var[ , "Variabilities"])
  
  esp <- arq_var[arq_var$Classificacao == "Especialista", ]
  mis <- arq_var[arq_var$Classificacao == "Misto", ]
  
  specialistByVariability <- ineq(esp$Variabilities, n = esp$Cumulativo, type = "Gini")
  specialistByVariability
  
  mixedByVariability <- ineq(mis$Variabilities, n = mis$Cumulativo, type = "Gini")
  mixedByVariability
  
  retorno <- data.frame(
    Projeto = projeto,
    specialistByVariability = specialistByVariability,
    mixedByVariability = mixedByVariability
  )
  
  return (retorno)
}
