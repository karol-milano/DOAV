#!/usr/bin/env Rscript

source("00_Utils.R")

tabelaComparacao <- function() {
  x <- data.frame()
  path <- "../data/graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaAutores(file.names[i])
    x <- rbind(x, gerarTabelaComparacao(file.names[i], valores))
  }
  
  write.table(x, file="../data/21_TabelaComparacao.csv", sep=",", row.names=F)
}


#' Função que gera a tabela TabelaComparacao
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarTabelaComparacao <- function(projeto, valores) {
  #projeto <- "Cherokee"
  #valores <- lerPlanilhaAutores(projeto)
  
  arq_var <- valores %>%
    select(Desenvolvedor, Classificacao, EhAutor)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Desenvolvedor", "Classificacao", "EhAutor")]), ]

  arq_var <- arq_var %>%
    summarise(Specialist = sum(Classificacao == "Especialista"),
              Generalist = sum(Classificacao == "Generalista"),
              Mixed = sum(Classificacao == "Misto")) %>%
    mutate(Project = projeto)
  
  arq_var <- arq_var %>%
    select(Project, everything())
  
  return (arq_var)
}
