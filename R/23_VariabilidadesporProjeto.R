source("00_Utils.R")

valores <- lerPlanilhaContagem()

arq_var <- valores %>%
  select(Projeto, Variabilidades_n)

imagem <- paste("../data/_VariabilidadesProjeto.png", sep = "")

png(file = imagem)

p <- arq_var %>%
  ggplot(aes(x = "", y = Variabilidades_n)) + 
  geom_violin(fill="lightskyblue", draw_quantiles = c(0.25, 0.5, 0.75)) +
  geom_boxplot(width = 0.1, fill = "lightskyblue1") +
  stat_summary(fun.data = n_fun, geom = "text", color = "red", size = 12) +
  theme(legend.position = "none") +
  labs(x = "Project", y = "Amount of Variabilities",
       title = "Variabilities per Project")

print(p)

dev.off()
