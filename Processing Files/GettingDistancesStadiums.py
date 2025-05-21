import pandas as pd
from geopy.distance import geodesic
from itertools import combinations

distance = pd.read_csv('address_lat_lon_ids.csv')

# Prepare list of all unique combinations of stadiums
stadium_pairs = list(combinations(distance.itertuples(index=False), 2))

# Calculate distances
distance_data = []
for team1, team2 in stadium_pairs:
    coord1 = (team1.latitude, team1.longitude)
    coord2 = (team2.latitude, team2.longitude)
    distance_miles = geodesic(coord1, coord2).miles
    distance_data.append({
        "Team_1": team1.Club,
        "Team_1_ID": team1.team_id,
        "Team_2": team2.Club,
        "Team_2_ID": team2.team_id,
        "Distance_miles": distance_miles
    })

# Convert to DataFrame
distance_df = pd.DataFrame(distance_data)

distance_df.to_csv('distancesBetweenStadiums.csv', index=False)