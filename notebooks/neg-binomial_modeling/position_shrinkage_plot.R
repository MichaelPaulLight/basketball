library(brms)
library(tidyverse)
library(ggrepel)

varying_slopes_model_constrained_real_2 <- readRDS("models/varying-slopes-model_negbinom_constrained_real_2.rds")

stratified_sample <- nanoparquet::read_parquet("stratified-sample_neg-binomial.parquet")

raw_position_rates <- stratified_sample %>%
  group_by(position) %>%
  summarize(
    n_observations = n(),
    total_shots = sum(offender_fga),
    raw_shot_rate = total_shots / n_observations
  )

position_effects <- ranef(varying_slopes_model_constrained_real_2, summary = TRUE)$position

position_intercepts <- position_effects[, , "Intercept"] %>%
  as.data.frame() %>%
  rownames_to_column("position") %>%
  mutate(
    # Convert log-scale effect to shot rate (assuming average values for other predictors)
    model_shot_rate = exp(1.6 + Estimate)
  )

position_shrinkage <- raw_position_rates %>%
  inner_join(position_intercepts, by = "position") %>%
  # Sort by raw shot rate for visualization
  arrange(raw_shot_rate)

position_shrinkage_plot <- ggplot(position_shrinkage, aes(x = raw_shot_rate, y = model_shot_rate)) +
  geom_point(aes(size = n_observations), alpha = 0.7) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "red") +
  geom_smooth(method = "lm", color = "blue", se = FALSE) +
  # Add labels for all positions (since there are only a few)
  geom_label_repel(
    aes(label = position),
    size = 3,
    fontface = "bold",
    box.padding = 0.5,
    point.padding = 0.3,
    force = 3,
    segment.color = "grey50",
    min.segment.length = 0
  ) +
  labs(
    title = "Shrinkage of Position Shot Rates",
    subtitle = "Model estimates vs. raw rates (point size indicates sample size)",
    x = "Raw Shot Rate per Observation",
    y = "Model-Estimated Shot Rate",
    size = "Number of\nObservations"
  ) +
  theme_minimal()

# Save the plot to the images directory
ggsave("../reporting/images/position_shrinkage.png", position_shrinkage_plot, width = 8, height = 6, dpi = 300)
