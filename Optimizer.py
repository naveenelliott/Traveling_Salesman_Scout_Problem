import pandas as pd
import ast
from collections import defaultdict
from pulp import *

# Load and clean data
df = pd.read_csv("joined_schedule_FINAL_MLS.csv")
df['Next_Team_Distances'] = df['Next_Team_Distances'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

# Build options list
options = []
for idx, row in df.iterrows():
    for next_team, dist, talent in row['Next_Team_Distances']:
        options.append({
            'id': idx,
            'match': f"{row['home_team']} vs {row['away_team']}",
            'date': row['Date'],
            'from_team': row['home_team'],
            'next_team': next_team,
            'distance': dist,
            'talent': talent,
            'next_date': row['Next_Date']
        })

# Create optimization model
model = LpProblem("Scout_Schedule_Optimization", LpMaximize)
x = {i: LpVariable(f"x_{i}", cat=LpBinary) for i in range(len(options))}

# Objective: Weight talent higher than distance
model += lpSum([x[i] * (10 * options[i]["talent"] - options[i]["distance"]) for i in range(len(options))])

# Constraint: No team scouted more than 4 times
team_appearances = defaultdict(list)
for i, opt in enumerate(options):
    team_appearances[opt["from_team"]].append(x[i])
    team_appearances[opt["next_team"]].append(x[i])
for team, vars_list in team_appearances.items():
    model += lpSum(vars_list) <= 4, f"TeamLimit_{team}"

# Constraint: Only one match per date
date_matches = defaultdict(list)
for i, opt in enumerate(options):
    date_matches[opt["date"]].append(x[i])
for date, vars_list in date_matches.items():
    model += lpSum(vars_list) <= 1, f"MaxOneMatch_{date}"

# Constraint: Enforce continuity
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
            if opt_j["next_team"] != opt_k["from_team"]:
                model += x[j] + x[k] <= 1, f"Disjoint_{j}_{k}"

# Solve model
model.solve()

# Collect results
final_schedule = []
total_distance = 0
total_talent = 0
for i, var in x.items():
    if var.value() == 1:
        final_schedule.append(options[i])
        total_distance += options[i]['distance']
        total_talent += options[i]['talent']

final_df = pd.DataFrame(final_schedule)

