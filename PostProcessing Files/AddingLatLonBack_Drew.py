import pandas as pd

final_df = pd.read_csv('Results/final_uslc_sched.csv')
del final_df['match_away_team'], final_df['team_score.y'], final_df['distance_km.y']

final_df.rename(columns={'match_id': 'match',
                         'corrected_next_team': 'next_home',
                         'match_home_team': 'from_team'}, inplace=True)

distance = pd.read_csv('address_lat_lon_ids.csv')
del distance['team_id']

distance = distance.rename(columns={
    col: f"{col}_from" for col in distance.columns if col != 'Club'
})

distance['Club'] = distance['Club'].str.lower()


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

distance_next['Club'] = distance_next['Club'].str.lower()

final_df = pd.merge(
    final_df,
    distance_next,
    left_on='next_home',
    right_on='Club'
)
del final_df['Club']

final_df = final_df[['match', 'date', 'from_team', 'latitude_from', 'longitude_from',
                     'next_home', 'latitude_next', 
                     'longitude_next', 'avg_talent']]

distance = pd.read_csv('distancesBetweenStadiums.csv')
del distance['Team_1_ID'], distance['Team_2_ID']

distance['Team_1'] = distance['Team_1'].str.lower()
distance['Team_2'] = distance['Team_2'].str.lower()

final_df = pd.merge(final_df, distance, left_on=['from_team', 'next_home'], right_on=['Team_1', 'Team_2'], how='left')

final_df = pd.merge(final_df, distance, left_on=['from_team', 'next_home'], right_on=['Team_2', 'Team_1'], how='left')

final_df['Distance_miles_x'] = final_df['Distance_miles_x'].fillna(final_df['Distance_miles_y'])

final_df.drop(columns={'Team_1_x', 'Team_2_x', 'Team_1_y', 'Team_2_y', 'Distance_miles_y'}, inplace=True)

final_df.rename(columns={'Distance_miles_x': 'distance'}, inplace=True)

final_df = final_df[['match', 'date', 'from_team', 'latitude_from', 'longitude_from',
                     'next_home', 'latitude_next', 'longitude_next', 'distance', 'avg_talent']]

final_df['distance'] = final_df['distance'].fillna(0)

final_df.to_csv('react_app_data_uslc.csv', index=False)