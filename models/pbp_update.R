library(hoopR)
library(tidyverse)
library(janitor)
library(zoo)
library(nanoparquet)

player_logs <- nba_leaguegamelog(season = "2024-25", player_or_team = "P") %>%
  pluck("LeagueGameLog") %>%
  clean_names() %>%
  mutate(team_location = ifelse(str_detect(matchup, "\\@"), "away", "home"),
         across(c(player_id, team_id), as.numeric))

existing_pbp <- list.files(path = "../data", 
                          pattern = "^\\d{6}_pbp_gt\\.parquet$", 
                          full.names = TRUE) |>
  sort(decreasing = TRUE) |>
  first() |>
  read_parquet()

function_pbp <- function(x){
  nba_data_pbp(x) %>%
    mutate(game_id = x)
}

games <- player_logs %>%
  distinct(game_id) %>%
  pull(game_id)

pbp_month <- map_df(games, function_pbp)