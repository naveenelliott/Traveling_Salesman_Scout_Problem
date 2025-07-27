library(worldfootballR)
library(dplyr)

# 1. Squad URL for Columbus Crew
team_url <- "https://www.transfermarkt.com/columbus-crew-sc/startseite/verein/813"

# 2. Get Squad Player URLs
squad <- tm_squad_stats(team_url)

# 3. Extract player URLs
player_urls <- squad$player_url

# 4. Start timing
start_time <- Sys.time()

# 5. Loop through each player and pull bio data
player_bios <- lapply(player_urls, function(url) {
  Sys.sleep(1.5)  # be polite to the server
  tryCatch(tm_player_bio(url), error = function(e) NULL)
})

# 6. Combine into a single data frame
bios_df <- do.call(bind_rows, player_bios)

# 7. End timing
end_time <- Sys.time()
total_time <- end_time - start_time

# 8. Output
cat("Scraping completed in", total_time, "seconds\n")
print(bios_df)
