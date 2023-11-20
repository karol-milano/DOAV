#Arquivos por Projeto 

source("00_Utils.R")


valores <- lerPlanilhaContagem()


imagem <- paste("../data/_ArquivoProjeto.png", sep = "")

valores %>%
# p <- valores %>%
  select(Projeto, Arquivo_n) %>%
  ggplot(aes(x = "", y = Arquivo_n)) +
  coord_trans(y="log10")+
  geom_violin(draw_quantiles = c(0.25, 0.5, 0.75)) +
  geom_boxplot(width = 0.1, alpha = 0.2) +
  geom_jitter(position = position_jitter(width = 0.2)) +
  stat_summary(fun.data = n_fun, geom = "point", color = "red", size = 2) +
  stat_summary(fun.data = n_fun, geom = "text", color = "red", size = 5) +
  theme_light() +
  theme(legend.position = "none") +
  labs(x = "Project", y = "Amount of File",
       title = "File per Project")
  
ggsave(imagem, p, dpi=600)