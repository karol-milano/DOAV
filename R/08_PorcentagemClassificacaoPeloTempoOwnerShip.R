#!/usr/bin/env Rscript

source("00_Utils.R")

porcentagemClassificacaoPeloTempo <- function() {
  path <- "../graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaCommits(file.names[i])
    gerarPorcentagemClassificacaoPeloTempoOwnerShip(file.names[i], valores)
  }
}


#' Função que gera o gráfico PorcentagemClassificacaoPeloTempo
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarPorcentagemClassificacaoPeloTempoOwnerShip <- function(projeto, valores) {
  #projeto <- "Uwsgi"
  #valores <- lerPlanilhaCommits(projeto)
  
  arq_var <- valores %>%
    select(Desenvolvedor, Data, Classificacao_ownership)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Data", "Desenvolvedor", "Classificacao_ownership")]), ]
  
  arq_var <- arq_var %>%
    arrange(Data, Desenvolvedor)
  
  nomes <- unique(arq_var$Desenvolvedor)
  
  x <- data.frame(matrix("", ncol = 1, nrow = length(nomes)), row.names = nomes)
  dimnames(x)[[2]] <- c("Valor")
  
  maj <- 0
  min <- 0
  
  idt <- 0
  dt <- ""
  for (i in 1:nrow(arq_var)) {
    nome <- arq_var[i, "Desenvolvedor"]
    
    if (arq_var[i, "Classificacao_ownership"] != x[nome, "Valor"]) {
      if (arq_var[i, "Classificacao_ownership"] == "Major") {
        maj <- maj + 1
      }
      else {
        min <- min + 1
      }
      
      if (x[nome, "Valor"] != "") {
        if (x[nome, "Valor"] == "Major") {
          maj <- maj - 1
        }
        else {
          min <- min - 1
        }
      }
      
      x[nome, "Valor"] <- arq_var[i, "Classificacao_ownership"]
    }
    
    if (dt != arq_var[i, "Data"]) {
      for (j in idt:i) {
        arq_var[j, "Major"] <- maj
        arq_var[j, "Minor"] <- min
        
        arq_var[j, "Total"] <- maj + min
        
        arq_var[j, "Perc_Major"] <- maj * 100 / arq_var[j, "Total"]
        arq_var[j, "Perc_Minor"] <- min * 100 / arq_var[j, "Total"]
      }
      
      idt <- i + 1
      dt <- arq_var[i, "Data"]
    }
  }

  df <- melt(arq_var, id.vars = "Data", variable.name = "Percentage", measure.vars = c("Perc_Major", "Perc_Minor"))
  df <- arrange(df, Data)
  
  tabela <- paste("../graphs/", projeto, "/08_", projeto, "_PercentageClassificationOverTimeOwnership.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../graphs/", projeto, "/08_", projeto, "_PercentageClassificationOverTimeOwnership.png", sep = "")
  
  png(file = imagem)
  
  p <- df %>%
    ggplot(aes(x = as.Date(Data), y = value, group = Percentage, color = Percentage)) +
    geom_line() +
    geom_point(alpha = 0.2, size = 0.5) +
    scale_x_date(date_labels = "%Y", date_breaks = "2 years", date_minor_breaks = "1 years") +
    theme(axis.text.x = element_text(angle=90),
          legend.position = "bottom") +
    labs(x = "", y = "Percentage of developers",
         title = "Developer Classification Over Time")
  
  print(p)
  
  dev.off()
}
