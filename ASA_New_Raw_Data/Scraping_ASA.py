from itscalledsoccer.client import AmericanSoccerAnalysis

asa_client = AmericanSoccerAnalysis()

gk_data = asa_client.get_goalkeeper_goals_added(leagues=["mls", "uslc", "usl1"], season_name="2025")

gk_data.to_csv("ASA_New_Raw_Data/gk_data.csv", index=False)

player_data = asa_client.get_player_goals_added(leagues=["mls", "uslc", "usl1"], season_name="2025")

player_data.to_csv("ASA_New_Raw_Data/player_goals_added.csv", index=False)

player_data2 = asa_client.get_player_xgoals(leagues=["mls", "uslc", "usl1"], season_name="2025")

player_data2.to_csv("ASA_New_Raw_Data/player_xgoals.csv", index=False)

player_data3 = asa_client.get_player_xpass(leagues=["mls", "uslc", "usl1"], season_name="2025")

player_data3.to_csv("ASA_New_Raw_Data/player_xpass.csv", index=False)

player_info = asa_client.get_players(leagues=["mls", "uslc", "usl1"])

player_info.to_csv("ASA_New_Raw_Data/player_info.csv", index=False)

stadium_data = asa_client.get_stadia(leagues=["mls", "uslc", "usl1"])

stadium_data.to_csv("ASA_New_Raw_Data/stadium_data.csv", index=False)

team_data = asa_client.get_teams(leagues=["mls", "uslc", "usl1"])
team_data.to_csv("ASA_New_Raw_Data/team_data.csv", index=False)