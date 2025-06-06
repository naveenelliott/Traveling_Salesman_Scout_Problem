import pandas as pd
import re
import ast
from collections import defaultdict

# Load and clean
df = pd.read_csv('joined_schedule_FINAL_USLC.csv')
df.drop(columns=['Score', 'home_talent', 'away_talent'], inplace=True)

def clean_and_eval(cell):
    if pd.isna(cell):
        return []
    # Remove np.float64 wrappers
    cleaned = re.sub(r'np\.float64\((.*?)\)', r'\1', cell)
    return ast.literal_eval(cleaned)

df['Next_Team_Distances'] = df['Next_Team_Distances'].apply(clean_and_eval)


# Determine "must scout" teams based on single viable game per day
all_dates = sorted(df['Date'].unique())
must_scout_counts = defaultdict(int)
for date in all_dates:
    games = df[df['Date'] == date]
    viable_games = []
    for _, row in games.iterrows():
        if any(dist > 0 for _, _, dist, _ in row['Next_Team_Distances']):
            viable_games.append(row)
    if len(viable_games) == 1:
        row = viable_games[0]
        must_scout_counts[row['home_team']] += 1
        must_scout_counts[row['away_team']] += 1

# Initialize
final_schedule = []
total_distance = 0
total_talent = 0
team_counts = defaultdict(int)

for team, count in must_scout_counts.items():
    team_counts[team] = count

# START: pick best opening game
first_day = df[df['Date'] == all_dates[0]]
best_row = first_day.loc[first_day['avg_talent'].idxmax()]
from_team = best_row['home_team']
next_date = best_row['Next_Date']
best_next_team, best_talent, best_distance = None, -1, None

for next_home, next_away, dist, talent in best_row['Next_Team_Distances']:
    if talent > best_talent and team_counts[next_home] < 5 and team_counts[next_away] < 5:
        best_next_team, best_talent, best_distance = (next_home, next_away), talent, dist

if best_next_team is None:
    for next_home, next_away, dist, talent in best_row['Next_Team_Distances']:
        if talent > best_talent:
            best_next_team, best_talent, best_distance = (next_home, next_away), talent, dist

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
total_talent += best_talent
team_counts[best_row['home_team']] += 1
team_counts[best_row['away_team']] += 1
current_team = best_next_team
current_date = next_date

# Continue the sequence
while current_date in df['Date'].values:
    next_day_games = df[df['Date'] == current_date]
    row = next_day_games[
        (next_day_games['home_team'].isin(current_team)) | 
        (next_day_games['away_team'].isin(current_team))
    ]
    
    if row.empty:
        break

    row = row.iloc[0]
    best_next = None
    best_score = -1
    
    valid_options = [
        (home, away, dist, talent) for home, away, dist, talent in row['Next_Team_Distances']
    ]



    for next_home, next_away, dist, talent in valid_options:
        penalty_home = 1 / (1 + team_counts[next_home])
        penalty_away = 1 / (1 + team_counts[next_away])
        
        penalty = (penalty_home + penalty_away) / 2
        score = (talent**2) / (dist + 1e-6) * penalty

        if score > best_score:
            best_next = {
                'Date': row['Date'],
                'Match': f"{row['home_team']} vs {row['away_team']}",
                'From_Team': current_team[0],
                'Current_Team': (next_home, next_away),
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
    total_talent += best_next['Talent']
    team_counts[best_next['Current_Team'][0]] += 1
    team_counts[best_next['Current_Team'][1]] += 1
    team_counts[row['home_team']] += 1
    team_counts[row['away_team']] += 1
    current_team = best_next['Current_Team']
    current_date = best_next['Next_Date']

# Final DataFrame adjustments
final_df = pd.DataFrame(final_schedule)

final_df.to_csv('Results/postOptimality_USLC.csv', index=False)

print('Total Talent: ', total_talent)

print('Total Distance: ', total_distance)

print("Team Appearance Counts:", dict(sorted(team_counts.items(), key=lambda x: -x[1])))