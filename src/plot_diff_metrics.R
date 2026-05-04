#install.packages(c("readxl", "tidyr", "ggplot2", "patchwork", "glue"))  # run once
library(readxl)
library(tidyr)
library(ggplot2)
library(patchwork)
library(glue)


make_heatmap <- function(lang, icd_code, plot_title, typeofmetrics, metric) {
  filepath <- glue("results/{lang}/{icd_code}/colored_metrics_{typeofmetrics}.xlsx")
  df <- read_excel(filepath)
  df <- as.data.frame(df)
  metric_names <- df[[1]]
  df <- df[,-1]
  df <- df[complete.cases(df), ]
  df[] <- lapply(df, function(x) as.numeric(as.character(x)))
  df_t <- as.data.frame(t(df))
  df_t <- df_t[complete.cases(df_t), ]
  df_t$model <- c(
    'lingconv', 'prism',
                  'ascle-bigbird-pegasus-1',
                  'ascle-bigbird-pegasus-2',
                  'ascle-biobart-1',
                  'ascle-biobart-2',
                  'ascle-bart-1',
                  'ascle-bart-2',
                  'biomistral-run0',
                  'biomistral-run1',
                  'biomistral-run2',
                  'biomistral-run3',
                  'biomistral-run4',
                  'biomistral-run5',
                  'biomistral-run6',
                  'biomistral-run7',
                  'biomistral-run8',
                  'biomistral-run9')
  
   df_long <- df_t %>%
    pivot_longer(
      cols = -model,
      names_to = "metric_index",
      values_to = "value"
    )
  metric_map <- setNames(metric_names, colnames(df_t)[-ncol(df_t)])
  df_long$metric <- metric_map[df_long$metric_index]
  df_long$metric <- factor(df_long$metric, levels = metric_names)

  df_long <- df_long[df_long$metric %in% metric, ]
  
  df_long$value[df_long$metric == "bleu"] <- df_long$value[df_long$metric == "bleu"] / 100
  
  p <- ggplot(df_long, aes(x = metric, y = model, fill = value)) +
    geom_tile(color = "white") +
    # geom_text(aes(label = round(value, 2))) +
    scale_fill_gradient(low = "firebrick1", high = "chartreuse1", name = "original -\n simplified") +
    scale_y_discrete(limits = rev(df_t$model)) +
    theme_minimal() +
    theme(
      text = element_text(size = 14),
      axis.text.x = element_text(angle = 25, hjust = 0.5),
      legend.title = element_text(size = 10),
      plot.title = element_text(hjust = 0.5)) +
    xlab("") +
    ylab("") +
    ggtitle(plot_title) +
    
    scale_x_discrete(labels = c(
      "diff_flesch_reading_ease" = "diff_fre",
      "diff_flesch_kincaid_grade" = "diff_fkgl",
      "diff_smog_index" = "diff_smog",
      "diff_gunning_fog" = "diff_fog",
      "diff_coleman_liau_index" = "diff_cli",
      "diff_automated_readability_index" = "diff_ari",
      "diff_dale_chall_readability_score" = "diff_dcr"
    ))
    
  return(p)
}

metrics <- c('diff_ttr', 'diff_mattr', 'diff_mtld',
             'diff_lix', 'diff_rix', 'diff_flesch_reading_ease')

metrics <- c('')

lang <- 'en'

metric_type <- 'complexity'

p1 <- make_heatmap(lang, "6A20", "6A20, en", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 2))

p2 <- make_heatmap(lang, "6A21", "6A21, en", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 0),
    axis.text.y = element_blank())

p3 <- make_heatmap(lang, "6A22", "6A22, en", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 0),
    axis.text.y = element_blank())

p4 <- make_heatmap(lang, "6A23", "6A23, en", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 0),
    axis.text.y = element_blank())

p5 <- make_heatmap(lang, "6A24", "6A24, en", metric_type, metrics) +
  theme(
    legend.position = "right",
    plot.margin = margin(2, 2, 2, 0),
    axis.text.y = element_blank())

lang <- 'de'

p6 <- make_heatmap(lang, "6A20", "6A20, de", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 2))
p6
p7 <- make_heatmap(lang, "6A21", "6A21, de", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 0),
    axis.text.y = element_blank())

p8 <- make_heatmap(lang, "6A22", "6A22, de", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 0),
    axis.text.y = element_blank())

p9 <- make_heatmap(lang, "6A23", "6A23, de", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 0),
    axis.text.y = element_blank())

p10 <- make_heatmap(lang, "6A24", "6A24, de", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 2, 2, 0),
    axis.text.y = element_blank())

lang <- 'fr'

p11 <- make_heatmap(lang, "6A20", "6A20, fr", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 2))

p12 <- make_heatmap(lang, "6A21", "6A21, fr", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 0),
    axis.text.y = element_blank())


p13 <- make_heatmap(lang, "6A22", "6A22, fr", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 0),
    axis.text.y = element_blank())

p14 <- make_heatmap(lang, "6A23", "6A23, fr", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 0, 2, 0),
    axis.text.y = element_blank())

p15 <- make_heatmap(lang, "6A24", "6A24, fr", metric_type, metrics) +
  theme(
    legend.position = "none",
    plot.margin = margin(2, 2, 2, 0),
    axis.text.y = element_blank())
  
# combined <-# Combine horizontally with smaller spacing
#   (p1 | p2) / 
#   (p3 | p5) + 
#   plot_layout(heights = c(2, 2))


combined <-# Combine horizontally with smaller spacing
  (p1 | p2 | p3 | p4 | p5) /
  (p6 | p7 | p8 | p9 | p10) /
  (p11 | p12 | p13 | p14 | p15) +
  plot_layout(guides = "collect",
              heights = c(4, 2, 2))


combined <-# Combine horizontally with smaller spacing
  (p1 | p2) /
  (p6 | p7) /
  (p11 | p12) +
  plot_layout(guides = "collect",
              heights = c(4, 2, 2))


combined <-# Combine horizontally with smaller spacing
  (p1 | p2 | p3 | p4 | p5) +
  plot_layout(guides = "collect")

combined


