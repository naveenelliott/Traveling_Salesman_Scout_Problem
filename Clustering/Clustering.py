import pandas as pd
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

df = pd.read_csv('ASA_New_Raw_Data/asa_data_FINAL.csv')

# Convert to datetime
df['birth_date'] = pd.to_datetime(df['birth_date'])

# Calculate age
today = pd.Timestamp(datetime.today())
df['Age'] = df['birth_date'].apply(lambda x: today.year - x.year - ((today.month, today.day) < (x.month, x.day)))

df.drop(columns={'birth_date', 'height_in', 'height_ft', 'weight_lb', 'minutes_played'}, inplace=True)

df.dropna(inplace=True)

info_columns = ['player_id', 'player_name', 'team_id', 'team_name']
df_info = df[info_columns]
df_cluster = df.drop(columns=info_columns, errors='ignore')


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
kmeans = KMeans(n_clusters=9, random_state=42)
df_info['Cluster'] = kmeans.fit_predict(scaled_data)