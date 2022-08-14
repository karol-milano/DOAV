#!/usr/bin/env Rscript

source("00_Utils.R")

arquivosPorDesenvolvedor <- function() {
  path <- "../graphs/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaAutores(file.names[i])
    gerarArquivosPorDesenvolvedor(file.names[i], valores)
  }
}


#' Função que gera o gráfico ArquivosPorDesenvolvedor
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarArquivosPorDesenvolvedor <- function(projeto, valores) {
  #projeto <- "Gawk"
  #valores <- lerPlanilhaAutores(projeto)
  
  arq_var <- valores %>%
    select(Arquivo, Desenvolvedor)
  
  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Arquivo", "Desenvolvedor")]), ]
  
  arq_var <- arq_var %>%
    group_by(Desenvolvedor) %>%
    summarise(Arquivo = n())
  
  tabela <- paste("../graphs/", projeto, "/02_", projeto, "_FilesPerDeveloper.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../graphs/", projeto, "/02_", projeto, "_FilesPerDeveloper.png", sep = "")
  
  png(file = imagem)
  
  p <- arq_var %>%
    ggplot(aes(x = "", y = Arquivo)) + 
    geom_violin(fill="lightskyblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
    geom_boxplot(width=0.1, fill="lightskyblue1") +
    stat_summary(fun.data = n_fun, geom = "text", size = 10) +
    theme(plot.title = element_text(size=22)) +
    labs(x = "Developer", y = "Amount of Files",
         title = "Files per developer")
  
  print(p)
  
  dev.off()
}
