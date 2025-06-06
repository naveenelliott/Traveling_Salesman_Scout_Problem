import pandas as pd
from fuzzywuzzy import process

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
    'St. Louis CITY SC': 'St. Louis CITY SC',
    'Toronto FC': 'Toronto FC'
}

reverse_name_mapping = {v: k for k, v in name_mapping.items()}

changed_schedule = schedule.copy()
changed_schedule['home_team'] = changed_schedule['home_team'].map(reverse_name_mapping)
changed_schedule['away_team'] = changed_schedule['away_team'].map(reverse_name_mapping)

# Sort the schedule by date
schedule['Date'] = pd.to_datetime(schedule['Date'])
schedule = schedule.sort_values('Date').reset_index(drop=True)

schedule['home_team'] = schedule['home_team'].map(reverse_name_mapping).fillna(schedule['home_team'])
schedule['away_team'] = schedule['away_team'].map(reverse_name_mapping).fillna(schedule['away_team'])

distance['team_key'] = distance.apply(
    lambda row: '___'.join(sorted([row['Team_1'], row['Team_2']])), axis=1
)
distance_lookup = dict(zip(distance['team_key'], distance['Distance_miles']))

# Ensure mapping
schedule['home_team'] = schedule['home_team'].map(reverse_name_mapping).fillna(schedule['home_team'])
schedule['away_team'] = schedule['away_team'].map(reverse_name_mapping).fillna(schedule['away_team'])

# Filter out rows with missing teams
schedule = schedule.dropna(subset=['home_team'])

# Get unique match days
unique_dates = sorted(schedule['Date'].dropna().unique())
distance_rows = []

for i in range(len(unique_dates) - 1):
    current_date = unique_dates[i]
    next_date = unique_dates[i + 1]

    current_group = schedule[schedule['Date'] == current_date].copy()
    next_group = schedule[schedule['Date'] == next_date].copy()

    for idx, row in current_group.iterrows():
        current_team = row['home_team']
        match_date = row['Date']

        # Build list of (next_team, distance) tuples
        tuples = []
        for next_team in next_group['home_team']:
            key = '___'.join(sorted([current_team, next_team]))
            distance = distance_lookup.get(key, None)
            tuples.append((next_team, distance))

        row['Next_Date'] = next_date
        row['Next_Team_Distances'] = tuples
        distance_rows.append(row)

# Combine all results
final_schedule = pd.DataFrame(distance_rows)

final_schedule['Next_Team_Distances'] = final_schedule['Next_Team_Distances'].apply(
    lambda lst: [(team, dist if dist is not None else 0) for team, dist in lst]
)

talent = pd.read_csv('top_11_talent.csv')

talent_teams = talent['Team'].unique()

schedule_teams = final_schedule['home_team'].unique()

team_mapping = {}
for messy_name in talent_teams:
    match, score = process.extractOne(messy_name, schedule_teams)
    team_mapping[messy_name] = match
    
talent['Team'] = talent['Team'].map(team_mapping)

# Merge total talent scores to map team → talent score
team_to_talent = talent.set_index('Team')['mean_talent'].to_dict()

final_schedule['home_talent'] = final_schedule['home_team'].map(team_to_talent).fillna(0)
final_schedule['away_talent'] = final_schedule['away_team'].map(team_to_talent).fillna(0)

final_schedule['avg_talent'] = (final_schedule['home_talent'] + final_schedule['away_talent'])/2

# Step 1: create a lookup for (date, team) → (home_talent, away_talent)
lookup = final_schedule.set_index(['Date', 'home_team'])[['home_talent', 'away_talent']].to_dict('index')

# Step 2: update the Next_Team_Distances list with full combined_talent
final_schedule['Next_Team_Distances'] = final_schedule.apply(
    lambda row: [
        (
            next_team,
            dist if dist is not None else 0,
            (lookup.get((row['Next_Date'], next_team), {}).get('home_talent', 0) +
            lookup.get((row['Next_Date'], next_team), {}).get('away_talent', 0))/2
        )
        for next_team, dist in row['Next_Team_Distances']
    ],
    axis=1
)

final_schedule.to_csv('joined_schedule_FINAL.csv', index=False)