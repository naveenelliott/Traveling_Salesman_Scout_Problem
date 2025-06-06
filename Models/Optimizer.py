import pandas as pd
import ast
from collections import defaultdict
from pulp import *

# Load data
df = pd.read_csv("joined_schedule_FINAL_MLS.csv")

def clean_and_eval(cell):
    if pd.isna(cell):
        return []
    # Remove np.float64 wrappers
    cleaned = re.sub(r'np\.float64\((.*?)\)', r'\1', cell)
    return ast.literal_eval(cleaned)

df['Next_Team_Distances'] = df['Next_Team_Distances'].apply(clean_and_eval)

# Construct optimization options
options = []
for idx, row in df.iterrows():
    for next_home, next_away, dist, talent in row['Next_Team_Distances']:
        options.append({
            'id': idx,
            'match': f"{row['home_team']} vs {row['away_team']}",
            'date': row['Date'],
            'from_team': row['home_team'],
            'away_team': row['away_team'],
            'next_home': next_home,
            'next_away': next_away,
            'distance': dist,
            'talent': talent,
            'next_date': row['Next_Date']
        })

# Create optimization model
model = LpProblem("Scout_Schedule_Optimization", LpMaximize)
x = {i: LpVariable(f"x_{i}", cat=LpBinary) for i in range(len(options))}

# Objective: Weight talent more than distance (talent^2 / (distance + 1))
model += lpSum([
    x[i] * ((options[i]["talent"]) / (options[i]["distance"] + 1e-6))
    for i in range(len(options))
])

manual_first_game = None
for i, opt in enumerate(options):
    if opt['date'] == '2025-05-24' and opt['match'] == 'Real Salt Lake City vs Vancouver Whitecaps FC':
        manual_first_game = i
        break

# Constraint: Only one match per date
date_matches = defaultdict(list)
for i, opt in enumerate(options):
    date_matches[opt["date"]].append(x[i])
for date, vars_list in date_matches.items():
    model += lpSum(vars_list) <= 1, f"MaxOneMatch_{date}"

# Constraint: Enforce continuity (next team's home matches must follow)
dates = sorted(set(opt["date"] for opt in options))
for i in range(len(dates) - 1):
    today = dates[i]
    tomorrow = dates[i + 1]
    for j, opt_j in enumerate(options):
        if opt_j["date"] != today:
            continue
        for k, opt_k in enumerate(options):
            if opt_k["date"] != tomorrow:
                continue
            if opt_j["next_home"] != opt_k["from_team"] and opt_j["next_home"] != opt_k["away_team"]:
                model += x[j] + x[k] <= 1, f"Disjoint_{j}_{k}"

if manual_first_game is not None:
    model += x[manual_first_game] == 1, "Force_First_Game"
    first_game_date = options[manual_first_game]['date']
    for i, opt in enumerate(options):
        if i != manual_first_game and opt['date'] == first_game_date:
            model += x[i] == 0, f"Block_Alt_FirstDate_{i}"

# Solve the model
model.solve()

# Extract the final schedule
final_schedule = []
total_distance = 0
total_talent = 0
for i, var in x.items():
    if var.value() == 1:
        final_schedule.append(options[i])
        total_distance += options[i]['distance']
        total_talent += options[i]['talent']

final_df = pd.DataFrame(final_schedule)

team_counts = defaultdict(int)
for _, row in final_df.iterrows():
    team_counts[row['from_team']] += 1
    team_counts[row['away_team']] += 1
    team_counts[row['next_home']] += 1
    team_counts[row['next_away']] += 1

print('Total Talent: ', total_talent)

print('Total Distance: ', total_distance)

print("Team Appearance Counts:", dict(sorted(team_counts.items(), key=lambda x: -x[1])))

final_df.to_csv('Results/optimizer_MLS.csv', index=False)

