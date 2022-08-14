#!/usr/bin/env Rscript

source("00_Utils.R")

classificacaoPeloTempo <- function() {
  path <- "../data/graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaCommits(file.names[i])
    gerarClassificacaoPeloTempo(file.names[i], valores)
  }
}


#' Função que gera o gráfico ClassificacaoPeloTempo
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarClassificacaoPeloTempo <- function(projeto, valores) {
  #projeto <- "Xterm"
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
  
  gen <- 0
  esp <- 0
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
      }
      
      idt <- i + 1
      dt <- arq_var[i, "Data"]
    }
  }
  
  df <- melt(arq_var, id.vars = "Data", variable.name = "Classificacao", measure.vars = c("Specialist", "Generalist", "Mixed"))
  df <- arrange(df, Data)

  tabela <- paste("../data/graphs/", projeto, "/05_", projeto, "_ClassificationOverTimeDOA.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../data/graphs/", projeto, "/05_", projeto, "_ClassificationOverTimeDOA.png", sep = "")
  
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
    # facet_wrap(~EhAutor, scales = "free_y", ncol = 1)
  
  print(p)
  
  dev.off()
}
