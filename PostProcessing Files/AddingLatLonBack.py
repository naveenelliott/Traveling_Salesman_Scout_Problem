import pandas as pd

final_df = pd.read_csv('Results/optimizer_MLS.csv')
del final_df['id'], final_df['away_team'], final_df['next_away']

distance = pd.read_csv('address_lat_lon_ids.csv')
del distance['team_id']

distance = distance.rename(columns={
    col: f"{col}_from" for col in distance.columns if col != 'Club'
})


final_df = pd.merge(
    final_df,
    distance,
    left_on='from_team',
    right_on='Club'
)
del final_df['Club']

# Reload distance to avoid overlapping renames
distance = pd.read_csv('address_lat_lon_ids.csv')
del distance['team_id']

# Rename columns (except 'Club') with _next
distance_next = distance.rename(columns={
    col: f"{col}_next" for col in distance.columns if col != 'Club'
})

final_df = pd.merge(
    final_df,
    distance_next,
    left_on='next_home',
    right_on='Club'
)
del final_df['Club']

final_df = final_df[['match', 'date', 'from_team', 'latitude_from', 'longitude_from',
                     'next_date', 'next_home', 'latitude_next', 
                     'longitude_next', 'distance', 'talent']]