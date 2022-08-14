#!/usr/bin/env Rscript

source("00_Utils.R")

porcentagemClassificacaoPeloTempo <- function() {
  path <- "../data/graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaCommits(file.names[i])
    gerarPorcentagemClassificacaoPeloTempoDOA(file.names[i], valores)
  }
}


#' Função que gera o gráfico PorcentagemClassificacaoPeloTempoDOA
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarPorcentagemClassificacaoPeloTempoDOA <- function(projeto, valores) {
  #projeto <- "Collected"
  #valores <- lerPlanilhaCommits(projeto)
  
  arq_var <- valores %>%
    select(Data, Desenvolvedor, Classificacao)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Data", "Desenvolvedor", "Classificacao")]), ]
  
  arq_var <- arq_var %>%
    arrange(Data, Desenvolvedor)
  
  nomes <- unique(arq_var$Desenvolvedor)
  
  x <- data.frame(matrix("", ncol = 1, nrow = length(nomes)), row.names = nomes)
  dimnames(x)[[2]] <- c("Valor")
  
  esp <- 0
  gen <- 0
  mis <- 0
  
  idt <- 0
  dt <- ""
  for (i in 1:nrow(arq_var)) {
    nome <- arq_var[i, "Desenvolvedor"]
    
    if (arq_var[i, "Classificacao"] != x[nome, "Valor"]) {
      if (arq_var[i, "Classificacao"] == "Especialista") {
        esp <- esp + 1
      }
      else if (arq_var[i, "Classificacao"] == "Generalista") {
        gen <- gen + 1
      }
      else {
        mis <- mis + 1
      }
      
      if (x[nome, "Valor"] != "") {
        if (x[nome, "Valor"] == "Especialista") {
          esp <- esp - 1
        }
        else if (x[nome, "Valor"] == "Generalista") {
          gen <- gen - 1
        }
        else {
          mis <- mis - 1
        }
      }
      
      x[nome, "Valor"] <- arq_var[i, "Classificacao"]
    }
    
    if (dt != arq_var[i, "Data"]) {
      for (j in idt:i) {
        arq_var[j, "Specialist"] <- esp
        arq_var[j, "Generalist"] <- gen
        arq_var[j, "Mixed"] <- mis
        
        arq_var[j, "Total"] <- esp + gen + mis
        
        arq_var[j, "Perc_Specialist"] <- esp * 100 / arq_var[j, "Total"]
        arq_var[j, "Perc_Generalist"] <- gen * 100 / arq_var[j, "Total"]
        arq_var[j, "Perc_Mixed"] <- mis * 100 / arq_var[j, "Total"]
      }
      
      idt <- i + 1
      dt <- arq_var[i, "Data"]
    }
  }
  
  df <- melt(arq_var, id.vars = "Data", variable.name = "Percentage", measure.vars = c("Perc_Specialist", "Perc_Generalist", "Perc_Mixed"))
  df <- arrange(df, Data)
  
  tabela <- paste("../data/graphs/", projeto, "/07_", projeto, "_PercentageClassificationOverTimeDOA.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../data/graphs/", projeto, "/07_", projeto, "_PercentageClassificationOverTimeDOA.png", sep = "")
  
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
    # facet_wrap(~EhAutor, scales = "free_y", ncol = 1)
  
  print(p)
  
  dev.off()
}
