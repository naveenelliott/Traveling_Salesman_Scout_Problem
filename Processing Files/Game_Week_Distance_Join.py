import pandas as pd
from rapidfuzz import process, fuzz

mls = pd.read_csv('mls_sched.csv')

usl_1 = pd.read_csv('usl1_sched.csv')

uslc = pd.read_csv('uslc_sched.csv')

schedule = pd.concat([mls, usl_1, uslc], ignore_index=True)

schedule.drop(columns=['home_xg', 'away_xg', 'Venue'], inplace=True)

schedule = schedule.loc[schedule['Score'].isna()]

# Convert 'Date' to datetime format
schedule['Date'] = pd.to_datetime(schedule['Date'], errors='coerce')

# Sort the DataFrame by date
schedule = schedule.sort_values('Date').reset_index(drop=True)

distance = pd.read_csv('distancesBetweenStadiums.csv')
del distance['Team_1_ID'], distance['Team_2_ID']

unique_distances = distance['Team_1'].unique()
unique_schedules = schedule['home_team'].unique()


name_mapping = {
    'AV Alta FC': 'AV Alta FC',
    'Austin FC': 'Austin FC',
    'Birmingham Legion FC': 'Birmingham Legion FC',
    'Charlotte Independence': "Charlotte Ind'ence",
    'Chattanooga Red Wolves SC': "Chat'ga Red Wolves",
    'Chicago Fire FC': 'Chicago Fire FC',
    'Detroit City FC': 'Detroit City FC',
    'El Paso Locomotive FC': 'El Paso Locomotive FC',
    'FC Naples': 'FC Naples',
    'Forward Madison FC': 'Fwd Madison',
    'Greenville Triumph SC': "G'ville Triumph",
    'Houston Dynamo FC': 'Houston Dynamo FC',
    'Indy Eleven': 'Indy Eleven',
    'Las Vegas Lights FC': 'Las Vegas Lights FC',
    'Los Angeles FC': 'Los Angeles FC',
    'Louisville City FC': 'Louisville City FC',
    'Miami FC': 'Miami FC',
    'Minnesota United FC': 'Minnesota United FC',
    'Monterey Bay FC': 'Monterey Bay FC',
    'Nashville SC': 'Nashville SC',
    'New Mexico United': 'New Mexico United',
    'Orange County SC': 'Orange County SC',
    'Pittsburgh Riverhounds FC': 'Pittsburgh Riverhounds FC',
    'Real Salt Lake City': 'Real Salt Lake City',
    'San Diego FC': 'San Diego FC',
    'Tampa Bay Rowdies': 'Tampa Bay Rowdies',
    'Texoma FC': 'Texoma FC',
    'Union Omaha': 'Union Omaha',
    'Vancouver Whitecaps FC': 'Vancouver Whitecaps FC',
    'Westchester SC': 'Westchester SC',
    'Atlanta United FC': 'Atlanta United FC',
    'CF Montreal': 'CF Montreal',
    'Charleston Battery': 'Charleston Battery',
    'Charlotte FC': 'Charlotte FC',
    'Colorado Rapids': 'Colorado Rapids',
    'Colorado Springs Switchbacks FC': 'Colorado Springs Switchbacks FC',
    'Columbus Crew': 'Columbus Crew',
    'D.C. United': 'D.C. United',
    'FC Cincinnati': 'FC Cincinnati',
    'FC Dallas': 'FC Dallas',
    'FC Tulsa': 'FC Tulsa',
    'Hartford Athletic': 'Hartford Athletic',
    'Inter Miami CF': 'Inter Miami CF',
    'Lexington SC': 'Lexington SC',
    'Los Angeles Galaxy': 'Los Angeles Galaxy',
    'Loudoun United FC': 'Loudoun United FC',
    'New England Revolution': 'New England Revolution',
    'New York City FC': 'New York City FC',
    'New York Red Bulls': 'New York Red Bulls',
    'North Carolina FC': 'North Carolina FC',
    'Oakland Roots SC': 'Oakland Roots SC',
    'One Knoxville SC': 'One Knoxville SC',
    'Orlando City FC': 'Orlando City FC',
    'Philadelphia Union': 'Philadelphia Union',
    'Phoenix Rising FC': 'Phoenix Rising FC',
    'Portland Hearts of Pine': 'Hearts of Pine',
    'Portland Timbers': 'Portland Timbers',
    'Rhode Island FC': 'Rhode Island FC',
    'Richmond Kickers': 'Richmond',
    'Sacramento Republic FC': 'Sacramento Republic FC',
    'San Antonio FC': 'San Antonio FC',
    'San Jose Earthquakes': 'San Jose Earthquakes',
    'Seattle Sounders FC': 'Seattle Sounders FC',
    'South Georgia Tormenta FC': 'Tormenta FC',
    'Spokane Velocity FC': 'Spokane Velocity FC',
    'Sporting Kansas City': 'Sporting Kansas City',
    'St. Louis CITY SC': 'St. Louis CITY SC'
}

reverse_name_mapping = {v: k for k, v in name_mapping.items()}

changed_schedule = schedule.copy()
changed_schedule['home_team'] = changed_schedule['home_team'].map(reverse_name_mapping)
changed_schedule['away_team'] = changed_schedule['away_team'].map(reverse_name_mapping)

# Sort the schedule by date
schedule['Date'] = pd.to_datetime(schedule['Date'])
schedule = schedule.sort_values('Date').reset_index(drop=True)

# Shift the schedule forward by 1 row to get the "next" match
schedule['Next_home_team'] = schedule['home_team'].shift(-1)
schedule['Next_Date'] = schedule['Date'].shift(-1)

# Merge distances from home team to next match's home team
distance_lookup = distance_df.copy()

# Create a unified lookup key for easier merging
distance_lookup['team_key'] = distance_lookup['Team_1'] + "___" + distance_lookup['Team_2']
schedule['team_key'] = schedule['home_team'] + "___" + schedule['Next_home_team']

# Merge based on this key
schedule = schedule.merge(distance_lookup[['team_key', 'Distance_miles']], how='left', on='team_key')

# Also check reverse direction if not found
missing_distances = schedule[schedule['Distance_miles'].isna()].copy()
missing_distances['team_key_rev'] = missing_distances['Next_home_team'] + "___" + missing_distances['home_team']
distance_lookup_rev = distance_lookup.copy()
distance_lookup_rev['team_key_rev'] = distance_lookup_rev['Team_2'] + "___" + distance_lookup_rev['Team_1']

# Merge reverse matches
missing_distances = missing_distances.merge(distance_lookup_rev[['team_key_rev', 'Distance_miles']], how='left', on='team_key_rev')

# Fill in the original schedule
schedule.loc[schedule['Distance_miles'].isna(), 'Distance_miles'] = missing_distances['Distance_miles_y'].values
