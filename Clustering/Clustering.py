import pandas as pd
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

df = pd.read_csv('Clustering/final_joined.csv')

df.dropna(inplace=True)

info_columns = ['player_name', 'rating', 'team_name', 'competition', 'Age']
df_info = df[info_columns]
df_cluster = df.drop(columns=info_columns, errors='ignore')


drop_columns = ['fouling_goals_added_above_avg_p90', 'shooting_goals_added_above_avg_p90', 'passing_goals_added_above_avg_p90', 
                'shooting_goals_added_above_avg_p90', 'dribbling_goals_added_above_avg_p90', 'receiving_goals_added_above_avg_p90', 
                'points_added_p90', 'xpoints_added_p90', 'goals_p90', 'Long ball accuracy_percentile', 'Cross accuracy_percentile',
                'Aerials won %_percentile', 'Dribbles success rate_percentile', 'goals_minus_xgoals_p90', 'Duels won %_percentile',
                'interrupting_goals_added_above_avg_p90', 'Fouls committed_percentile', 'Tackles won %_percentile', 'avg_distance_yds_p90',
                'xpass_completion_percentage', 'Dribbled past_percentile', 'Interceptions_percentile', 'primary_assists_minus_xassists_p90',
                'passes_completed_over_expected_p100', 'shots_on_target_p90', 'primary_assists_p90', 'attempted_passes_p90',
                'avg_vertical_distance_yds_p90', 'Chances created_percentile', 'xassists_p90', 'Dispossessed_percentile', 'Blocked scoring attempt_percentile',
                'Duels won_percentile', 'Fouls won_percentile', 'Accurate long balls_percentile',
                'Tackles won_percentile', 'Recoveries_percentile', 'Possession won final 3rd_percentile', 'xgoals_p90']

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
kmeans = KMeans(n_clusters=8, random_state=42)
df_info['Cluster'] = kmeans.fit_predict(scaled_data)

# Merge scaled data and cluster labels into a DataFrame
clustered_df = pd.DataFrame(scaled_data, columns=df_cluster.columns)
clustered_df['Cluster'] = df_info['Cluster']

# Calculate mean feature values for each cluster
cluster_means = clustered_df.groupby('Cluster').mean()

percentile_df = cluster_means.rank(pct=True) * 100
percentile_df = percentile_df.round(1)

df_info.loc[df_info['competition'] == 'mls', 'adjustment'] = 1
df_info.loc[df_info['competition'] == 'uslc', 'adjustment'] = (63.7/78.31)
df_info.loc[df_info['competition'] == 'usl1', 'adjustment'] = (56.19/78.31)

df_info['rating'] = df_info['rating'] * df_info['adjustment']

# Z-score of adjusted rating within each cluster
df_info['cluster_rating_zscore'] = df_info.groupby('Cluster')['rating'].transform(
    lambda x: (x - x.mean()) / x.std(ddof=0)
)

# Percentile rank of adjusted rating within each cluster
df_info['cluster_rating_percentile'] = df_info.groupby('Cluster')['rating'].rank(pct=True) * 100
df_info['cluster_rating_percentile'] = df_info['cluster_rating_percentile'].round(1)

cluster_name = {
        2 : 'Creative 9s',
        1 : 'Progressive Passers in Def 3rd',
        0 : 'High Volume Goalscorers',
        7 : 'Progressive Dribblers in Def 3rd',
        5 : '10s',
        3 : 'Attacking FBs',
        4 : 'No-Nonsense Defender',
        6 : 'Difference Makers'
    }

df_info['Cluster Name'] = df_info['Cluster'].map(cluster_name)

def categorize_age(age):
    if age < 21:
        return 'young'
    elif 21 <= age <= 25:
        return 'promising'
    elif 25 <= age <= 31:
        return 'prime'
    else:
        return 'Veteran'
    
df_info['Age Group'] = df_info['Age'].apply(categorize_age)

df_info.to_csv('clustering_FINAL.csv', index=False)







