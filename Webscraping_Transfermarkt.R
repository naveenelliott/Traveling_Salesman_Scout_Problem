#install.packages("devtools")
#devtools::install_github("JaseZiv/worldfootballR")

library(worldfootballR)


mls_mkt_values <- tm_player_market_values(start_year = 2024, 
                                          league_url='https://www.transfermarkt.us/major-league-soccer/startseite/wettbewerb/MLS1')

uslc_mkt_values <- tm_player_market_values(country_name="", start_year = 2024, 
                                          league_url='https://www.transfermarkt.us/usl-championship/startseite/wettbewerb/USL')

usl1_mkt_values = tm_player_market_values(country_name="", start_year = 2024, 
                                          league_url='https://www.transfermarkt.us/usl-league-one/startseite/wettbewerb/USC3')