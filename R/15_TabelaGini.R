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
  
  mean_row <- c("Mean", mean(x[,2]), mean(x[,3]), mean(x[,4]))
  x <- rbind(x, mean_row)
  
  write.table(x, file="../data/15_TabelaGini.csv", sep=",", row.names=F)
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
    select(Desenvolvedor, Commit)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Desenvolvedor", "Commit")]), ]
  
  arq_var <- arq_var %>%
    group_by(Desenvolvedor) %>%
    summarise(Commits = n())
  
  arq_var[ , "Cumulativo"] = cumsum(arq_var[ , "Commits"])
  
  commitsByDeveloper <- ineq(arq_var$Commits, n = arq_var$Cumulativo, type = "Gini")
  commitsByDeveloper
  
  ##############################################################################
  ##### Variabilidades por Desenvolvedor
  ##############################################################################
  
  arq_var <- valores %>%
    select(Desenvolvedor, Variabilidades)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Desenvolvedor", "Variabilidades")]), ]
  arq_var <- arq_var[!apply(arq_var, 1, function(x) any(x=="")), ]
  
  varpdes <- arq_var %>%
    group_by(Desenvolvedor) %>%
    summarise(Variabilidades = n())
  
  varpdes[ , "Cumulativo"] = cumsum(varpdes[ , "Variabilidades"])
  
  variabilitiesByDeveloper <- ineq(varpdes$Variabilidades, n = varpdes$Cumulativo, type = "Gini")
  variabilitiesByDeveloper
  
  ##############################################################################
  ##### Desenvolvedores por Variabilidade
  ##############################################################################
  
  despvar <- arq_var %>%
    group_by(Variabilidades) %>%
    summarise(Developers = n())
  
  despvar[ , "Cumulativo"] = cumsum(despvar[ , "Developers"])
  
  developersByVariability <- ineq(despvar$Developers, n = despvar$Cumulativo, type = "Gini")
  developersByVariability
  
  ##############################################################################
  ##############################################################################
  
  retorno <- data.frame(
    Projeto = projeto,
    CommitsByDeveloper = commitsByDeveloper,
    VariabilitiesByDeveloper = variabilitiesByDeveloper,
    DevelopersByVariability = developersByVariability
  )
  
  return (retorno)
}
