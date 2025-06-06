library(lubridate)
library(tidyverse)

sched <- read_csv("joined_schedule_FINAL.csv")

# Remove brackets to parse through distance data
parse_distances <- function(s) {
  s_clean <- str_remove_all(s, "\\[|\\]")
  items <- str_split(s_clean, "\\), \\(")[[1]]
  
  map(items, function(item) {
    parts <- str_remove_all(item, "'|\\(|\\)") %>%
      str_split(",\\s*") %>%
      unlist()
    
    list(
      team = parts[1],
      distance_km = as.numeric(parts[2]),
      distance_score = as.numeric(parts[3])
    )})}

# create match ids + find best first game
sched1 <- sched %>%
  mutate(
    match_id = paste(home_team, "vs", away_team),
    date = as.Date(Date),
    Next_Team_Distances_Parsed = map(Next_Team_Distances, parse_distances)
  )

all_dates <- unique(sched1$date)
first_gameday <- sched1$date[1]

best_first_game <- sched1 %>%
  filter(date == first_gameday) %>%
  filter(avg_talent == max(avg_talent)) %>%
  pull(match_id)


# Flatten schedule to show all combos

flattened <- sched1 %>%
  select(match_id, date, avg_talent, Next_Team_Distances_Parsed) %>%
  unnest(Next_Team_Distances_Parsed) %>%
  mutate(match_home_team = str_trim(str_to_lower(str_split_fixed(match_id, " vs ", 2)[, 1])),
         next_team = map_chr(Next_Team_Distances_Parsed, 1),
         distance_km = map_dbl(Next_Team_Distances_Parsed, 2),
         team_score = map_dbl(Next_Team_Distances_Parsed, 3)) %>%
  select(-Next_Team_Distances_Parsed)


# Make optimization function (50/50 emphasis)

objective_fn <- function(x, talent, distances, w_talent = 0.5, w_dist = 0.5) {
  total_score <- x * (w_talent * talent - w_dist * distances)
  return(-sum(total_score))
}

flattened <- flattened %>%
  mutate(scaled_talent = rescale(team_score),
         scaled_distance = rescale(log(distance_km + 1)))

# Make loop #

selected_games <- list()
current_team <- str_trim(str_to_lower("Real Salt Lake City"))  #starting team (vs. Whitecaps 5/24)

for (d in sort(unique(flattened$date))) {
  
  df_day <- flattened %>%
    filter(date == d, match_home_team == current_team)
  
  if (nrow(df_day) == 0) {
    df_day <- flattened %>%
      filter(date == d, match_home_team == current_team | match_away_team == current_team)
  }
  if (nrow(df_day) == 0) next  # If no match found
  
  # then just find best applicable match
  options <- diag(1, nrow(df_day))
  scores <- apply(options, 1, function(x) {
    -sum(x * (0.5 * df_day$scaled_talent - 0.5 * df_day$scaled_distance))
  })
  
  best_row <- which.min(scores)
  selected <- df_day[best_row, ]
  selected_games[[length(selected_games) + 1]] <- selected
  
  # Next team now current
  current_team <- str_trim(str_to_lower(selected$next_team))
}
# Final optimized schedule
schedule_proposal3 <- bind_rows(selected_games)




