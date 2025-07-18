import pandas as pd
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

df = pd.read_csv('Clustering/final_joined.csv')

df.dropna(inplace=True)

info_columns = ['player_name']
df_info = df[info_columns]
df_cluster = df.drop(columns=info_columns, errors='ignore')


drop_columns = ['fouling_goals_added_above_avg_p90', 'shooting_goals_added_above_avg_p90', 'passing_goals_added_above_avg_p90', 
                'shooting_goals_added_above_avg_p90', 'dribbling_goals_added_above_avg_p90', 'receiving_goals_added_above_avg_p90', 
                'points_added_p90', 'xpoints_added_p90', 'rating', 'goals_p90', 'Long ball accuracy_percentile', 'Cross accuracy_percentile',
                'Aerials won %_percentile', 'Dribbles success rate_percentile', 'goals_minus_xgoals_p90', 'Duels won %_percentile',
                'interrupting_goals_added_above_avg_p90', 'Fouls committed_percentile', 'Tackles won %_percentile', 'avg_distance_yds_p90',
                'xpass_completion_percentage', 'Dribbled past_percentile', 'Interceptions_percentile', 'primary_assists_minus_xassists_p90',
                'passes_completed_over_expected_p100', 'share_team_touches', 'shots_on_target_p90', 'primary_assists_p90', 'attempted_passes_p90',
                'Aerials won_percentile', 'avg_vertical_distance_yds_p90', 'Chances created_percentile', 'xassists_p90', 'Dispossessed_percentile',
                'Duels won_percentile', 'Recoveries_percentile']

df_cluster.drop(columns=drop_columns, inplace=True)

# Standardize the data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(df_cluster)

# Calculate inertia for different numbers of clusters
inertia = []
k_range = range(1, 19)
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(scaled_data)
    inertia.append(kmeans.inertia_)

# Plot the elbow plot
plt.figure(figsize=(8, 5))
plt.plot(k_range, inertia, marker='o')
plt.title('Elbow Plot for KMeans Clustering')
plt.xlabel('Number of Clusters (k)')
plt.ylabel('Inertia')
plt.grid(True)
plt.tight_layout()
plt.show()


# Fit KMeans with 7 clusters
kmeans = KMeans(n_clusters=7, random_state=42)
df_info['Cluster'] = kmeans.fit_predict(scaled_data)

# Merge scaled data and cluster labels into a DataFrame
clustered_df = pd.DataFrame(scaled_data, columns=df_cluster.columns)
clustered_df['Cluster'] = df_info['Cluster']

# Calculate mean feature values for each cluster
cluster_means = clustered_df.groupby('Cluster').mean()

# Standard deviation of feature means across clusters
between_cluster_std = cluster_means.std()

# Sort to find least-separated features
least_separated = between_cluster_std.sort_values()