#Arquivos por Projeto 

source("00_Utils.R")

give.n <- function(x){
  return (data.frame(y = median(x)*1.25, label = floor(median(x))))
  # experiment with the multiplier to find the perfect position
}

valores <- lerPlanilhaContagem()
valores$Commit_n <- as.integer(valores$Commit_n)

class(valores$Projeto)
class(valores$Arquivo_n)
class(valores$Desenvolvedor_n)
class(valores$Commit_n)
class(valores$Variabilidades_n)

valores <- valores[complete.cases(valores), ]

############ Arquivos por Projeto ############
imagem <- "../data/_ArquivoProjeto.svg"

a <- valores %>%
#valores %>%
  select(Projeto, Arquivo_n) %>%
  ggplot(aes(x = "", y = Arquivo_n)) +
  coord_trans(y="log10")+
  geom_violin(fill = "lightblue",draw_quantiles = c(0.25, 0.5, 0.75)) +
  #geom_violin() +
  geom_boxplot(width = 0.1, alpha = 0.2) +
  geom_jitter(position = "jitter", aes(colour = "blue", alpha = 0.2)) +
  stat_summary(fun.data = n_fun, geom = "point", color = "red", size = 2) +
  stat_summary(fun.data = give.n, geom = "text", color = "red", size = 4) +
  theme_linedraw() +
  theme(legend.position = "none") +
  labs(x = "Project", y = "# of Files",
       title = "Files per Project")

#ggsave(filename = imagem, plot = p, device = "svg")


############ Commits por Projeto ############
imagem <- "../data/_CommitsProjeto.svg"

c <- valores %>%
#valores %>%
  select(Projeto, Commit_n) %>%
  ggplot(aes(x = "", y = Commit_n)) +
  coord_trans(y="log10")+
  geom_violin(fill = "lightblue",draw_quantiles = c(0.25, 0.5, 0.75)) +
  #geom_violin() +
  geom_boxplot(width = 0.1, alpha = 0.2) +
  geom_jitter(position = "jitter", aes(colour = "blue", alpha = 0.2)) +
  stat_summary(fun.data = n_fun, geom = "point", color = "red", size = 2) +
  stat_summary(fun.data = give.n, geom = "text", color = "red", size = 4) +
  theme_linedraw() +
  theme(legend.position = "none") +
  labs(x = "Project", y = "# of Commits",
       title = "Commits per Project")

#ggsave(filename = imagem, plot = p, device = "svg")

############ Variabilidades por Projeto ############

imagem <- "../data/_VariabilidadesProjeto.svg"

v <- valores %>%
  #valores %>%
  select(Projeto, Variabilidades_n) %>%
  ggplot(aes(x = "", y = Variabilidades_n)) +
  coord_trans(y="log10")+
  geom_violin(fill = "lightblue",draw_quantiles = c(0.25, 0.5, 0.75)) +
  #geom_violin() +
  geom_boxplot(width = 0.1, alpha = 0.2) +
  geom_jitter(position = "jitter", aes(colour = "blue", alpha = 0.2)) +
  stat_summary(fun.data = n_fun, geom = "point", color = "red", size = 2) +
  stat_summary(fun.data = give.n, geom = "text", color = "red", size = 4) +
  theme_linedraw() +
  theme(legend.position = "none") +
  labs(x = "Project", y = "# of Variabilities",
       title = "Variabilities per Project")

#ggsave(filename = imagem, plot = p, device = "svg")

############ Desenvolvedores por Projeto ############

imagem <- "../data/_DesenvolvedoresProjeto.svg"

d <- valores %>%
#valores %>%
  select(Projeto, Desenvolvedor_n) %>%
  ggplot(aes(x = "", y = Desenvolvedor_n)) +
  coord_trans(y="log10")+
  geom_violin(fill = "lightblue",draw_quantiles = c(0.25, 0.5, 0.75)) +
  #geom_violin() +
  geom_boxplot(width = 0.1, alpha = 0.2) +
  geom_jitter(position = "jitter", aes(colour = "blue", alpha = 0.2)) +
  stat_summary(fun.data = n_fun, geom = "point", color = "red", size = 2) +
  stat_summary(fun.data = give.n, geom = "text", color = "red", size = 4) +
  theme_linedraw() +
  theme(legend.position = "none") +
  labs(x = "Project", y = "# of Developers",
       title = "Developers per Project")

#ggsave(filename = imagem, plot = p, device = "svg")

imagem <- "~/DesenvolvedoresProjeto.svg"

ggsave(filename = imagem, plot = arrangeGrob(a, c, d, v), device = "svg")
