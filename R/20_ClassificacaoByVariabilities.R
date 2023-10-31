#!/usr/bin/env Rscript

source("00_Utils.R")

desenvolvedoresPorVariabilidadePeloTempo <- function() {
  path <- "../data/graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaCommits(file.names[i])
    gerarDesenvolvedoresPorVariabilidadePeloTempo(file.names[i], valores)
  }
}


#' Função que gera o gráfico DesenvolvedoresPorVariabilidadePeloTempo
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarDesenvolvedoresPorVariabilidadePeloTempo <- function(projeto, valores) {
  projeto <- "irssi"
  valores <- lerPlanilhaCommits(projeto)
  
  arq_var <- valores %>%
    select(Classificacao, Data, Desenvolvedor, Variabilidades)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Desenvolvedor", "Data", "Variabilidades")]), ]
  arq_var <- arq_var[!apply(arq_var, 1, function(x) any(x=="")), ]
  #arq_var <- arq_var[!arq_var$Classificacao == "Generalista", ]
  
  arq_var <- arq_var %>%
    group_by(Variabilidades, Data, Classificacao) %>%
    summarise(Desenvolvedor = n())
  
  esp <- arq_var[arq_var$Classificacao == "Especialista", ]
  mix <- arq_var[arq_var$Classificacao == "Misto", ]
  
  tabela <- paste("../data/graphs/", projeto, "/20_", projeto, "_ClassificacaoByVariabilities.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  if (nrow(esp) > 0) {
    imagem <- paste("../data/graphs/", projeto, "/20_", projeto, "SpecialistsByVariabilities_.png", sep = "")
    
    png(file = imagem)
    
    pesp <- esp %>%
      ggplot(aes(x = "", y = Desenvolvedor)) +
      geom_violin(fill="lightskyblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
      geom_boxplot(width=0.1, fill="lightskyblue1") +
      coord_trans(y="log10") +
      stat_summary(fun.data = n_fun, geom = "text", size = 12) +
      theme(legend.position = "none") +
      labs(x = "", y = "Amount of Variabilities",
           title = "Specialists By Variabilities")
    
    print(pesp)
    
    dev.off()
  }
  
  if (nrow(mix) > 0) {
    imagem <- paste("../data/graphs/", projeto, "/20_", projeto, "MixedByVariabilities_.png", sep = "")
    
    png(file = imagem)
    
    pmix <- mix %>%
      ggplot(aes(x = "", y = Desenvolvedor)) +
      geom_violin(fill="lightskyblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
      geom_boxplot(width=0.1, fill="lightskyblue1") +
      coord_trans(y="log10") +
      stat_summary(fun.data = n_fun, geom = "text", size = 12) +
      theme(legend.position = "none") +
      labs(x = "", y = "Amount of Variabilities",
           title = "Mixed By Variabilities")
    
    print(pmix)
    
    dev.off()
  }
}
