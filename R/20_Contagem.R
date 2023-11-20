#!/usr/bin/env Rscript

source("00_Utils.R")

x <- data.frame()
path <- "../data/graphs/"

file.names <- c("busybox", "collectd", "curl", "dia", "emacs", "gcc", "glibc", "gnuplot", "hexchat", "irssi", "libexpat", "libsoup", "libssh-mirror", "libxml2", "lighttpd1.4", "mapserver", "marlin", "mongo", "openssl", "openvpn", "ossec-hids", "retroarch", "totem", "uwsgi", "xorg-xserver")

#file.names <- dir(path)
for (i in 1:length(file.names)) {
  valores <- lerPlanilhaCommits(file.names[i])
  #valores <- lerPlanilhaCommits("GCC")
  
  arq_var <- valores %>%
    summarise(Arquivo_n = length(unique(Arquivo)),
              Desenvolvedor_n = length(unique(Desenvolvedor)),
              Commit_n = length(unique(Commit)),
              Variabilidades_n = length(unique(Variabilidades)),
              Data_extracao = max(Data)) %>%
    mutate(Projeto = file.names[i])
  
  arq_var <- arq_var %>%
    select(Projeto, everything())
  
  x <- rbind(x, arq_var)
}

write.table(x, file="Contagem.csv", sep=",", row.names=F)
