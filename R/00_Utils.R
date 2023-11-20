#!/usr/bin/env Rscript

library(ineq)
library(dplyr)
library(readr)
library(ggplot2)
library(reshape2)


#' Função que encontra a média
#' 
#' @param data.frame x
#' @return Novo data.frame contendo a média
n_fun <- function(x) {
  return (data.frame(y = median(x), label = floor(median(x))))
}


#' Função que lê a planilha "Autores" do arquivo
#' 
#' @param projeto O nome do projeto que possui o arquivo de dados
#' @return Os valores lidos da planilha "Autores" do arquivo
lerPlanilhaAutores <- function(projeto) {
  arquivo <- paste("../data/graphs/", projeto, "/", projeto, "_authors.csv", sep = "")
  
  print(paste("Lendo o arquivo", arquivo))
  valores <- read.csv(arquivo)
  dimnames(valores)[[2]] <- c(
    "Desenvolvedor", 
    "Arquivo", 
    "Qtd_variabilidades", 
    "Existencia_TRUE", 
    "Variabilidades", 
    "Qtd_commits", 
    "Commits", 
    "DOA_A", 
    "DOA_N", 
    "Classificacao", 
    "EhAutor")
  
  return (valores)
}


#' Função que lê a planilha "Commits" do arquivo
#' 
#' @param projeto O nome do projeto que possui o arquivo de dados
#' @return Os valores lidos da planilha "Commits" do arquivo
lerPlanilhaCommits <- function(projeto) {
  arquivo <- paste("../data/graphs/", projeto, "/", projeto, "_commits.csv", sep = "")
  
  print(paste("Lendo arquivo", arquivo))
  valores <- read.csv(arquivo)
  dimnames(valores)[[2]] <- c(
    "Commit",
    "Data",
    "Desenvolvedor",
    "Arquivo",
    "Qtd_variabilidades",
    "Existencia_TRUE",
    "Variabilidades",
    "Classificacao",
    "EhAutor",
    "Ownership",
    "Classificacao_ownership",
    "Ownership_Final",
    "Classificacao_ownership_Final"
  )
  
  return (valores)
}


#' Função que lê a planilha "Variabilidades" do arquivo
#' 
#' @param projeto O nome do projeto que possui o arquivo de dados
#' @return Os valores lidos da planilha "Variabilidades" do arquivo
lerPlanilhaVariabilidades <- function(projeto) {
  arquivo <- paste("../data/graphs/", projeto, "/", projeto, "_variabilities.csv", sep = "")
  
  print(paste("Lendo o arquivo", arquivo))
  valores <- read.csv(arquivo)
  dimnames(valores)[[2]] <- c(
    "Desenvolvedor", 
    "Variabilidade", 
    "fa_geral",
    "Qtd_commits_geral", 
    "Qtd_commits_dl", 
    "Qtd_commits_ac", 
    "Qtd_arquivos", 
    "Arquivo", 
    "Qtd_commits_arquivo", 
    "fa_arquivo", 
    "Ownership_perc",
    "Ownership_n",
    "Ownership_geral",
    "Ownership_geral_n",
    "Ownership_arquivo",
    "Ownership_arquivo_n",
    "Ownership_rlm",
    "Ownership_rlm_n")
  
  return (valores)
}

lerPlanilhaContagem <-function()
{
  arquivo <- paste("Contagem.csv", sep = "")
  
  print(paste("Lendo arquivo", arquivo))
  valores <- read.csv(arquivo)
  dimnames(valores)[[2]] <- c(
    "Projeto",
    "Arquivo_n",
    "Desenvolvedor_n",
    "Commit_n",
    "Variabilidades_n",
    "Data_extracao")
  
  return (valores)
}

