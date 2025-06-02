import pandas as pd
import ast

# Load and clean
df = pd.read_csv('joined_schedule_FINAL.csv')
del df['Score'], df['home_talent'], df['away_talent']
df['Next_Team_Distances'] = df['Next_Team_Distances'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

# Sort dates
all_dates = sorted(df['Date'].unique())
final_schedule = []
total_distance = 0

# START: pick the game on the first date with the best average talent in Next_Team_Distances
first_day = df[df['Date'] == all_dates[0]]
best_row = first_day.loc[first_day['avg_talent'].idxmax()]  # ← selects best row directly

from_team = best_row['home_team']
next_date = best_row['Next_Date']
best_next_team = None
best_talent = -1
best_distance = None

for next_team, dist, talent in best_row['Next_Team_Distances']:
    if talent > best_talent:
        best_next_team = next_team
        best_talent = talent
        best_distance = dist

# Finalize starting entry
best_start = {
    'Date': best_row['Date'],
    'Match': f"{best_row['home_team']} vs {best_row['away_team']}",
    'From_Team': from_team,
    'Current_Team': best_next_team,
    'Distance': best_distance,
    'Talent': best_talent,
    'Next_Date': next_date
}

# Add to schedule
final_schedule.append(best_start)
total_distance += best_distance
current_team = best_next_team
current_date = next_date


# Continue sequentially by following the previous Current_Team
while current_date in df['Date'].values:
    next_day_games = df[df['Date'] == current_date]
    row = next_day_games[next_day_games['home_team'] == current_team]
    if row.empty:
        break

    row = row.iloc[0]

    best_next = None
    best_ratio = -1
    for next_team, dist, talent in row['Next_Team_Distances']:
        if dist > 0:
            ratio = talent / dist
            if ratio > best_ratio:
                best_next = {
                    'Date': row['Date'],
                    'Match': f"{row['home_team']} vs {row['away_team']}",
                    'From_Team': current_team,
                    'Current_Team': next_team,
                    'Distance': dist,
                    'Talent': talent,
                    'Ratio': ratio,
                    'Next_Date': row['Next_Date']
                }
                best_ratio = ratio

    if best_next is None:
        break

    final_schedule.append(best_next)
    total_distance += best_next['Distance']
    current_team = best_next['Current_Team']
    current_date = best_next['Next_Date']

# Build final DataFrame
final_df = pd.DataFrame(final_schedule)

final_df['Match'] = final_df['Match'].shift(-1)

print("Total Distance Traveled:", round(total_distance, 2))
