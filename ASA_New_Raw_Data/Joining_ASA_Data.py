import pandas as pd
import glob
import os
import ast

gk_data = pd.read_csv('ASA_New_Raw_Data/gk_data.csv')

player_ga = pd.read_csv('ASA_New_Raw_Data/player_goals_added.csv')

player_ga['data'] = player_ga['data'].apply(ast.literal_eval)

# Function to flatten each player's data
def flatten_player_actions(row):
    flat = {}
    for action in row['data']:
        prefix = action['action_type'].lower()
        flat[f"{prefix}_goals_added_above_avg"] = action['goals_added_above_avg']
        flat[f"{prefix}_count_actions"] = action['count_actions']
    flat['player_id'] = row['player_id']
    flat['team_id'] = row['team_id']
    return pd.Series(flat)

# Apply the function row-wise to flatten each player's data
wide_df = player_ga.apply(flatten_player_actions, axis=1)

wide_df.drop(columns={'shooting_count_actions'}, inplace=True)

player_xg = pd.read_csv('ASA_New_Raw_Data/player_xgoals.csv')
player_xg = player_xg[['player_id', 'team_id', 'general_position', 'shots',
       'shots_on_target', 'goals', 'xgoals', 'goals_minus_xgoals',
       'key_passes', 'primary_assists', 'xassists',
       'primary_assists_minus_xassists', 'points_added', 'xpoints_added']]


player_xp = pd.read_csv('ASA_New_Raw_Data/player_xpass.csv')
del player_xp['count_games'], player_xp['general_position'], player_xp['passes_completed_over_expected']

player_info = pd.read_csv('ASA_New_Raw_Data/player_info.csv')

player_info = player_info[['player_id', 'player_name', 'birth_date', 
       'height_ft', 'height_in', 'weight_lb']]

player_data = pd.merge(wide_df, player_xg, on=['player_id', 'team_id'], how='inner')

player_data = pd.merge(player_data, player_xp, on=['player_id', 'team_id'], how='inner')

player_data = pd.merge(player_info, player_data, on=['player_id'], how='inner')


stadium_data = pd.read_csv('ASA_New_Raw_Data/stadium_data.csv')

team_data = pd.read_csv('ASA_New_Raw_Data/team_data.csv')

del team_data['team_short_name'], team_data['team_abbreviation'], team_data['competition'] 


player_data = pd.merge(player_data, team_data, on='team_id', how='left')

gaaa_cols = [col for col in player_data.columns if col.endswith('goals_added_above_avg')]

for col in gaaa_cols:
    new_col = col + '_p90'
    player_data[new_col] = pd.to_numeric(player_data[col], errors='coerce') / pd.to_numeric(player_data['minutes_played'], errors='coerce') * 90

player_data.drop(columns=gaaa_cols, inplace=True)

p90 = ['shots', 'shots_on_target', 'goals', 'xgoals', 'goals_minus_xgoals', 'key_passes', 'primary_assists',
       'xassists', 'primary_assists_minus_xassists', 'points_added', 'xpoints_added', 'avg_distance_yds',
       'avg_vertical_distance_yds', 'attempted_passes']

for col in p90:
    new_col = col + '_p90'
    player_data[new_col] = pd.to_numeric(player_data[col], errors='coerce') / pd.to_numeric(player_data['minutes_played'], errors='coerce') * 90
    
player_data.drop(columns=p90, inplace=True)

count_cols = ['dribbling_count_actions', 'fouling_count_actions', 'interrupting_count_actions', 
              'passing_count_actions', 'receiving_count_actions']

for col in count_cols:
    player_data[col] = pd.to_numeric(player_data[col], errors='coerce') / pd.to_numeric(player_data['minutes_played'], errors='coerce') * 90
    
player_data.drop(columns=count_cols, inplace=True)

player_data.to_csv('ASA_New_Raw_Data/asa_data_FINAL.csv', index=False)