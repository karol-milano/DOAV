#!/usr/bin/env Rscript

source("00_Utils.R")

arquivosPorCommit <- function() {
  path <- "resultados/"
  file.names <- dir(path)
  for (i in 1:length(file.names)) {
    valores <- lerPlanilhaCommits(file.names[i])
    gerarArquivosPorCommit(file.names[i], valores)
  }
}


#' Função que gera o gráfico ArquivosPorCommit
#' 
#' @param projeto O nome do projeto em que será feito a análise
#' @param valores Os dados lidos do arquivo
gerarArquivosPorCommit <- function(projeto, valores) {
  #projeto <- "Gawk"
  #valores <- lerPlanilhaCommits(projeto)
  
  arq_var <- valores %>%
    select(Commit, Arquivo, EhAutor)

  arq_var <- arq_var[complete.cases(arq_var), ]
  arq_var <- arq_var[!duplicated(arq_var[, c("Commit", "Arquivo")]), ]
  
  arq_var <- arq_var %>%
    group_by(Commit, EhAutor) %>%
    summarise(Arquivo = n())
  
  arq_var <- arrange(arq_var, Arquivo)
  
  tabela <- paste("../data/graphs/", projeto, "/02_", projeto, "_FilesPerCommit.csv", sep = "")
  
  write.table(arq_var, file=tabela, sep=",", row.names=F)
  
  imagem <- paste("../data/graphs/", projeto, "/02_", projeto, "_FilesPerCommit.png", sep = "")
  
  png(file = imagem)
  
  p <- arq_var %>%
    ggplot(aes(x = "", y = Arquivo)) + 
    geom_violin(fill="lightskyblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
    geom_boxplot(width=0.1, fill="lightskyblue1") +
    stat_summary(fun.data = n_fun, geom = "text", color = "red", size = 10) +
    theme(legend.position = "none") +
    labs(x = "Commits", y = "Amount of Files",
         title = "Files per commit"
    )
  
  print(p)
  
  dev.off()
  
}
