import pandas as pd
import ast
from collections import defaultdict

# Load and clean
df = pd.read_csv('joined_schedule_FINAL_MLS.csv')
df.drop(columns=['Score', 'home_talent', 'away_talent'], inplace=True)
df['Next_Team_Distances'] = df['Next_Team_Distances'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

# Determine "must scout" teams based on single viable game per day
all_dates = sorted(df['Date'].unique())
must_scout_counts = defaultdict(int)
for date in all_dates:
    games = df[df['Date'] == date]
    viable_games = []
    for _, row in games.iterrows():
        if any(dist > 0 for _, dist, _ in row['Next_Team_Distances']):
            viable_games.append(row)
    if len(viable_games) == 1:
        row = viable_games[0]
        must_scout_counts[row['home_team']] += 1
        must_scout_counts[row['away_team']] += 1

# Initialize
final_schedule = []
total_distance = 0
team_counts = defaultdict(int)

for team, count in must_scout_counts.items():
    team_counts[team] = count

# START: pick best opening game
first_day = df[df['Date'] == all_dates[0]]
best_row = first_day.loc[first_day['avg_talent'].idxmax()]
from_team = best_row['home_team']
next_date = best_row['Next_Date']
best_next_team, best_talent, best_distance = None, -1, None

for next_team, dist, talent in best_row['Next_Team_Distances']:
    if talent > best_talent and team_counts[next_team] < 4:
        best_next_team, best_talent, best_distance = next_team, talent, dist

if best_next_team is None:
    for next_team, dist, talent in best_row['Next_Team_Distances']:
        if talent > best_talent:
            best_next_team, best_talent, best_distance = next_team, talent, dist

best_start = {
    'Date': best_row['Date'],
    'Match': f"{best_row['home_team']} vs {best_row['away_team']}",
    'From_Team': from_team,
    'Current_Team': best_next_team,
    'Distance': best_distance,
    'Talent': best_talent,
    'Next_Date': next_date
}

final_schedule.append(best_start)
total_distance += best_distance
team_counts[best_row['home_team']] += 1
team_counts[best_row['away_team']] += 1
current_team = best_next_team
current_date = next_date

# Continue the sequence
while current_date in df['Date'].values:
    next_day_games = df[df['Date'] == current_date]
    row = next_day_games[next_day_games['home_team'] == current_team]
    
    if row.empty:
        break

    row = row.iloc[0]
    best_next = None
    best_score = -1
    
    valid_options = [(t, d, ta) for t, d, ta in row['Next_Team_Distances'] if d >= 0 and team_counts[t] < 4]

    forced_over_limit = False
    if not valid_options:
        valid_options = [(t, d, ta) for t, d, ta in row['Next_Team_Distances'] if d >= 0]
        forced_over_limit = True  # flag to identify fallback scenario
    


    for next_team, dist, talent in valid_options:
        if dist <= 0:
            continue
        # Penalty logic
        if team_counts[next_team] >= 4:
            penalty = 0.1
        if team_counts[next_team] == 3:
            penalty = 0.3
        elif team_counts[next_team] == 2:
            penalty = 0.5
        elif team_counts[next_team] == 1:
            penalty = 0.7
        else:
            penalty = 1.0

        freshness_weight = 1 / (1 + team_counts[next_team])
        score = ((talent ** 2) / dist) * freshness_weight * penalty

        if score > best_score:
            best_next = {
                'Date': row['Date'],
                'Match': f"{row['home_team']} vs {row['away_team']}",
                'From_Team': current_team,
                'Current_Team': next_team,
                'Distance': dist,
                'Talent': talent,
                'Score': score,
                'Next_Date': row['Next_Date']
            }
            best_score = score
            

    if best_next is None:
        break

    final_schedule.append(best_next)
    total_distance += best_next['Distance']
    team_counts[row['home_team']] += 1
    team_counts[row['away_team']] += 1
    current_team = best_next['Current_Team']
    current_date = best_next['Next_Date']
    
    if forced_over_limit and team_counts[next_team] >= 4:
        print(f"{best_next['Date']} → {next_team} already scouted {team_counts[next_team]} times\n")

# Final DataFrame adjustments
final_df = pd.DataFrame(final_schedule)
final_df['Match'] = final_df['Match'].shift(-1)
final_df['Date'] = final_df['Date'].shift(-1)
final_df['Next_Date'] = final_df['Next_Date'].shift(-1)

# Results
print("Total Distance Traveled:", round(total_distance, 2))
print("Team Appearance Counts:", dict(sorted(team_counts.items(), key=lambda x: -x[1])))