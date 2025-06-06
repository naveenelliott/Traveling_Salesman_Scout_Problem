import pandas as pd
from fuzzywuzzy import process
from sklearn.preprocessing import MinMaxScaler
import numpy as np

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

nah = True

if nah == False:
    schedule_mls = schedule.loc[~(
        (schedule['Date'] == pd.Timestamp('2025-06-12')) &
        (schedule['home_team'] == 'New York City FC') &
        (schedule['away_team'] == 'Atlanta United FC')
    )]
    
    schedule_mls = schedule_mls.loc[~(
        (schedule_mls['Date'] == pd.Timestamp('2025-07-06')) &
        (schedule_mls['home_team'] == 'Seattle Sounders FC') &
        (schedule_mls['away_team'] == 'Columbus Crew')
    )]
    
    schedule_mls = schedule_mls.loc[~(
        (schedule_mls['Date'] == pd.Timestamp('2025-09-01')) &
        (schedule_mls['home_team'] == 'Los Angeles FC') &
        (schedule_mls['away_team'] == 'San Diego FC')
    )]
    
    schedule_mls = schedule_mls.loc[~(
        (schedule_mls['Date'] == pd.Timestamp('2025-09-16')) &
        (schedule_mls['home_team'] == 'Inter Miami CF') &
        (schedule_mls['away_team'] == 'Seattle Sounders FC')
    )]
    
    schedule_mls = schedule_mls.loc[~(
        (schedule_mls['Date'] == pd.Timestamp('2025-09-19')) &
        (schedule_mls['home_team'] == 'New York City FC') &
        (schedule_mls['away_team'] == 'Charlotte FC')
    )]
    
    schedule_mls = schedule_mls.loc[~(
        (schedule_mls['Date'] == pd.Timestamp('2025-09-24')) &
        (schedule_mls['home_team'] == 'New York City FC') &
        (schedule_mls['away_team'] == 'Inter Miami CF')
    )]
else:
    schedule_mls = schedule.copy()

# Get unique match days
unique_dates = sorted(schedule_mls['Date'].dropna().unique())
distance_rows = []

for i in range(len(unique_dates) - 1):
    current_date = unique_dates[i]
    next_date = unique_dates[i + 1]

    current_group = schedule_mls[schedule_mls['Date'] == current_date].copy()
    next_group = schedule_mls[schedule_mls['Date'] == next_date].copy()

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

final_schedule_mls = final_schedule[final_schedule['avg_talent'] >= 0.45].copy()

# Step 1: create a lookup for (date, team) → (home_talent, away_talent)
lookup = final_schedule_mls.set_index(['Date', 'home_team'])[['home_talent', 'away_talent']].to_dict('index')

# Step 2: update the Next_Team_Distances list with full combined_talent
# Rebuild distances only among filtered high-talent matchdays
distance_rows = []
unique_dates = sorted(final_schedule_mls['Date'].dropna().unique())

for i in range(len(unique_dates) - 1):
    current_date = unique_dates[i]
    next_date = unique_dates[i + 1]

    current_group = final_schedule_mls[final_schedule_mls['Date'] == current_date].copy()
    next_group = final_schedule_mls[final_schedule_mls['Date'] == next_date].copy()

    for idx, row in current_group.iterrows():
        current_team = row['home_team']
        row_copy = row.copy()
        row_copy['Next_Date'] = next_date

        tuples = []
        for _, next_row in next_group.iterrows():
            next_home = next_row['home_team']
            next_away = next_row['away_team']
            
            # Distance from current_team to next_home (primary anchor)
            key = '___'.join(sorted([current_team, next_home]))
            dist = distance_lookup.get(key, 0)
            
            avg_talent = (
                team_to_talent.get(next_home, 0) + team_to_talent.get(next_away, 0)
            ) / 2
            if avg_talent >= 0.45:
                tuples.append((next_home, next_away, dist, avg_talent))

        # Only keep the row if it has valid next teams
        if tuples:
            row_copy['Next_Team_Distances'] = tuples
            distance_rows.append(row_copy)

# Rebuild final_schedule
final_schedule_mls = pd.DataFrame(distance_rows)

def scale_distance_and_talent(df, col_name='Next_Team_Distances'):
    """
    Scales distance inversely (lower = closer to 1) and talent directly (higher = closer to 1)
    in a column of (home_team, away_team, distance, talent) tuples.
    """
    # Flatten all tuples
    all_tuples = [tup for lst in df[col_name] if lst for tup in lst]
    distances = [t[2] for t in all_tuples]
    talents = [t[3] for t in all_tuples]

    # Convert to arrays and scale
    dist_scaled = 1 - MinMaxScaler().fit_transform(np.array(distances).reshape(-1, 1)).flatten()
    talent_scaled = MinMaxScaler().fit_transform(np.array(talents).reshape(-1, 1)).flatten()

    # Rebuild scaled tuples
    scaled_tuples = list(zip(
        [t[0] for t in all_tuples],   # home_team
        [t[1] for t in all_tuples],   # away_team
        dist_scaled,
        talent_scaled
    ))

    # Rebuild list-of-lists structure
    pointer = 0
    scaled_lists = []
    for lst in df[col_name]:
        count = len(lst)
        scaled_lists.append(scaled_tuples[pointer:pointer+count])
        pointer += count

    df[col_name] = scaled_lists
    return df

final_schedule_mls = scale_distance_and_talent(final_schedule_mls)

final_schedule_mls.to_csv('joined_schedule_FINAL_MLS.csv', index=False)

final_schedule_uslc = final_schedule[final_schedule['avg_talent'] < 0.51].copy()

# Step 1: create a lookup for (date, team) → (home_talent, away_talent)
lookup = final_schedule_uslc.set_index(['Date', 'home_team'])[['home_talent', 'away_talent']].to_dict('index')

# Step 2: update the Next_Team_Distances list with full combined_talent
# Rebuild distances only among filtered high-talent matchdays
distance_rows = []
unique_dates = sorted(final_schedule_uslc['Date'].dropna().unique())

for i in range(len(unique_dates) - 1):
    current_date = unique_dates[i]
    next_date = unique_dates[i + 1]

    current_group = final_schedule_uslc[final_schedule_uslc['Date'] == current_date].copy()
    next_group = final_schedule_uslc[final_schedule_uslc['Date'] == next_date].copy()

    for idx, row in current_group.iterrows():
        current_team = row['home_team']
        row_copy = row.copy()
        row_copy['Next_Date'] = next_date

        tuples = []
        for _, next_row in next_group.iterrows():
            next_home = next_row['home_team']
            next_away = next_row['away_team']
            
            # Distance from current_team to next_home (primary anchor)
            key = '___'.join(sorted([current_team, next_home]))
            dist = distance_lookup.get(key, 0)
            
            avg_talent = (
                team_to_talent.get(next_home, 0) + team_to_talent.get(next_away, 0)
            ) / 2
            if avg_talent < 0.51:
                tuples.append((next_home, next_away, dist, avg_talent))

        # Only keep the row if it has valid next teams
        if tuples:
            row_copy['Next_Team_Distances'] = tuples
            distance_rows.append(row_copy)

# Rebuild final_schedule
final_schedule_uslc = pd.DataFrame(distance_rows)

final_schedule_uslc = scale_distance_and_talent(final_schedule_uslc)

final_schedule_uslc.to_csv('joined_schedule_FINAL_USLC.csv', index=False)

final_schedule_usl1 = final_schedule[final_schedule['avg_talent'] < 0.43].copy()

# Step 1: create a lookup for (date, team) → (home_talent, away_talent)
lookup = final_schedule_usl1.set_index(['Date', 'home_team'])[['home_talent', 'away_talent']].to_dict('index')

# Step 2: update the Next_Team_Distances list with full combined_talent
# Rebuild distances only among filtered high-talent matchdays
distance_rows = []
unique_dates = sorted(final_schedule_usl1['Date'].dropna().unique())

for i in range(len(unique_dates) - 1):
    current_date = unique_dates[i]
    next_date = unique_dates[i + 1]

    current_group = final_schedule_usl1[final_schedule_usl1['Date'] == current_date].copy()
    next_group = final_schedule_usl1[final_schedule_usl1['Date'] == next_date].copy()

    for idx, row in current_group.iterrows():
        current_team = row['home_team']
        row_copy = row.copy()
        row_copy['Next_Date'] = next_date

        tuples = []
        for _, next_row in next_group.iterrows():
            next_home = next_row['home_team']
            next_away = next_row['away_team']
            
            # Distance from current_team to next_home (primary anchor)
            key = '___'.join(sorted([current_team, next_home]))
            dist = distance_lookup.get(key, 0)
            
            avg_talent = (
                team_to_talent.get(next_home, 0) + team_to_talent.get(next_away, 0)
            ) / 2
            if avg_talent < 0.43:
                tuples.append((next_home, next_away, dist, avg_talent))
        # Only keep the row if it has valid next teams
        if tuples:
            row_copy['Next_Team_Distances'] = tuples
            distance_rows.append(row_copy)

# Rebuild final_schedule
final_schedule_usl1 = pd.DataFrame(distance_rows)

final_schedule_usl1 = scale_distance_and_talent(final_schedule_usl1)

final_schedule_usl1.to_csv('joined_schedule_FINAL_USL1.csv', index=False)