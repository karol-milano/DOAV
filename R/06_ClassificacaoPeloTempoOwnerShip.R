#!/usr/bin/env Rscript

source("00_Utils.R")

classificacaoPeloTempo <- function() {
  path <- "../graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaCommits(file.names[i])
    gerarClassificacaoPeloTempoOwnership(file.names[i], valores)
  }
}


#' Função que gera o gráfico ClassificacaoPeloTempo utilizando o ownership
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarClassificacaoPeloTempoOwnership <- function(projeto, valores) {
  #projeto <- "Bison"
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
      }
      
      idt <- i + 1
      dt <- arq_var[i, "Data"]
    }
  }
  
  df <- melt(arq_var, id.vars = "Data", variable.name = "Classificacao", measure.vars = c("Major", "Minor"))
  df <- arrange(df, Data)
  
  tabela <- paste("../graphs/", projeto, "/06_", projeto, "_ClassificationOverTimeOwnership.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../graphs/", projeto, "/06_", projeto, "_ClassificationOverTimeOwnerShip.png", sep = "")
  
  png(file = imagem)
  
  p <- df %>%
    ggplot(aes(x = as.Date(Data), y = value, group = Classificacao, color = Classificacao)) +
    geom_line() + 
    geom_point(alpha = 0.5, size = 0.75) +
    scale_x_date(date_labels = "%Y", date_breaks = "2 years", date_minor_breaks = "1 years") +
    theme(axis.text.x = element_text(angle=90),
          legend.position = "bottom") +
    labs(x = "", y = "Amount of Developers",
         title = "Classification Over Time")
  
  print(p)
  
  dev.off()
}
