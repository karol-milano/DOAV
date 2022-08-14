#!/usr/bin/env Rscript

source("00_Utils.R")

# Os arquivos a seguir utilizam a função lerPlanilhaAutores
source("01_VariabilidadesPorArquivo.R")
source("02_ArquivosPorDesenvolvedor.R")
source("16_TabelaComparacao.R")

# Os arquivos a seguir utilizam a função lerPlanilhaCommits
source("02_ArquivosPorCommit.R")
source("05_ClassificacaoPeloTempo.R")
source("06_ClassificacaoPeloTempoOwnerShip.R")
source("07_PorcentagemClassificacaoPeloTempoDOA.R")
source("08_PorcentagemClassificacaoPeloTempoOwnerShip.R")
source("09_VariabilidadesPorDesenvolvedorPeloTempo.R")
source("10_LCCommitsPorDesenvolvedor.R")
source("11_LCVariabilidadesPorDesenvolvedor.R")
source("12_DesenvolvedoresPorVariabilidadePeloTempo.R")
source("13_LCDesenvolvedoresPorCommitPeloTempoOwnerShip.R")
source("14_LCDesenvolvedoresPorVariabilidade.R")
source("15_TabelaGini.R")
source("17_DesenvolvedoresPorArquivo.R")

# ======================================================================= #

path <- "../data/graphs/"
file.names <- dir(path)
for (i in 1:length(file.names)) {
  projeto <- file.names[i]
  valores <- lerPlanilhaAutores(projeto)
  
  print(projeto)
  
  #   01_VariabilidadesPorArquivo
  print("|_ 01_gerarVariabilidadesPorArquivo")
  gerarVariabilidadesPorArquivo(projeto, valores)
  
  #   02_ArquivosPorDesenvolvedor
  print("|_ 02_gerarArquivosPorDesenvolvedor")
  gerarArquivosPorDesenvolvedor(projeto, valores)
  
  print("")  
# ======================================================================= #
  
  valores <- lerPlanilhaCommits(projeto)
  
  #   02_ArquivosPorCommit
  print("|_ 02_gerarArquivosPorCommit")
  gerarArquivosPorCommit(projeto, valores)
  
  #   05_ClassificacaoPeloTempo
  print("|_ 05_gerarClassificacaoPeloTempo")
  gerarClassificacaoPeloTempo(projeto, valores)
  
  #   06_ClassificacaoPeloTempoOwnerShip
  print("|_ 06_gerarClassificacaoPeloTempoOwnerShip")
  gerarClassificacaoPeloTempoOwnership(projeto, valores)
  
  #   07_PorcentagemClassificacaoPeloTempoDOA
  print("|_ 07_gerarPorcentagemClassificacaoPeloTempoDOA")
  gerarPorcentagemClassificacaoPeloTempoDOA(projeto, valores)
  
  #   08_PorcentagemClassificacaoPeloTempoOwnership
  print("|_ 08_PorcentagemClassificacaoPeloTempoOwnership")
  gerarPorcentagemClassificacaoPeloTempoOwnerShip(projeto, valores)
  
  #   09_VariabilidadesPorDesenvolvedorPeloTempo
  print("|_ 09_gerarVariabilidadesPorDesenvolvedorPeloTempo")
  gerarVariabilidadesPorDesenvolvedorPeloTempo(projeto, valores)
  
  #   10_LCCommitsPorDesenvolvedor
  print("|_ 10_gerarLCCommitsPorDesenvolvedor")
  gerarLCCommitsPorDesenvolvedor(projeto, valores)
  
  #   11_LCVariabilidadePorDesenvolvedor
  print("|_ 11_gerarLCVariabilidadePorDesenvolvedor")
  gerarLCVariabilidadesPorDesenvolvedor(projeto, valores)
  
  #   12_DesenvolvedoresPorVariabilidadePeloTempo
  print("|_ 12_gerarDesenvolvedoresPorVariabilidadePeloTempo")
  gerarDesenvolvedoresPorVariabilidadePeloTempo(projeto, valores)
  
  #   13_LCDesenvolvedoresPorCommitPeloTempoOwnership
  print("|_ 13_gerarLCDesenvolvedoresPorCommitPeloTempoOwnership")
  gerarLCDesenvolvedoresPorCommitPeloTempo(projeto, valores)
  
  #   14_LCDesenvolvedoresPorVariabilidade
  print("|_ 14_gerarLCDesenvolvedoresPorVariabilidade")
  gerarLCDesenvolvedoresPorVariabilidade(projeto, valores)
  
  #   17_DesenvolvedoresPorArquivo
  print("|_ 17_gerarDesenvolvedoresPorArquivo")
  gerarDesenvolvedoresPorArquivo(projeto, valores)
  
  print("")
  print("# ======================================================================= #")
  print("")
}

# ======================================================================= #
#   15_TabelaGini
print("|_ 15_gerarTabelaGini")
tabelaGini()

# ======================================================================= #
#   16_TabelaComparacao
print("|_ 16_gerarTabelaComparacao")
tabelaComparacao()

print("[DONE]")
