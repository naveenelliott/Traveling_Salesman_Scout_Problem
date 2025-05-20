import pandas as pd
import os
import glob

folder_path = 'Location_Raw_Data'

dfs = []
for file_path in glob.glob(os.path.join(folder_path, '*.csv')):
    # Read the CSV file
    df = pd.read_csv(file_path)
    dfs.append(df)
    
location_data = pd.concat(dfs, ignore_index=True)

# Forward-fill club names down the rows
location_data['Club'] = location_data['Club'].fillna(method='ffill')

# Group by club and concatenate address lines
clean_df = (
    location_data.groupby('Club')['Address']
    .apply(lambda x: ', '.join(x.dropna()))
    .reset_index()
    .rename(columns={'Address': 'Full_Address'})
)

clean_df.to_csv('club_addresses.csv', index=False)