import pandas as pd
import ast

df = pd.read_csv('joined_schedule_FINAL.csv')

del df['Score'], df['home_talent'], df['away_talent']

# Build the final schedule selecting one best game per day based on best talent/distance ratio
final_schedule = []


def parse_tuple_list(s):
    try:
        return ast.literal_eval(s)
    except:
        return []

# Parse the 'Next_Team_Distances' column
df['Next_Team_Distances'] = df['Next_Team_Distances'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

final_schedule = []
total_distance = 0

for date in sorted(df['Date'].unique()):
    day_games = df[df['Date'] == date]

    best_talent = -1
    best_entry = {}

    for _, row in day_games.iterrows():
        next_date = row['Next_Date']
        next_day_teams = set(df[df['Date'] == next_date][['home_team', 'away_team']].values.ravel())

        for from_team in [row['home_team'], row['away_team']]:
            for next_team, dist, talent in row['Next_Team_Distances']:
                if next_team in next_day_teams and talent > best_talent:
                    # Look up the actual match that next_team is in
                    next_game = df[
                        (df['Date'] == next_date) &
                        ((df['home_team'] == next_team) | (df['away_team'] == next_team))
                    ].iloc[0]

                    best_entry = {
                        'Date': date,
                        'Match': f"{next_game['home_team']} vs {next_game['away_team']}",
                        'From_Team': from_team,
                        'Current_Team': next_team,
                        'Distance': dist,
                        'Talent': talent
                    }
                    best_talent = talent

    if best_entry:
        final_schedule.append(best_entry)
        total_distance += best_entry['Distance']

final_df = pd.DataFrame(final_schedule)

final_df['From_Team'] = final_df['Current_Team'].shift(1).fillna(final_df['From_Team'])