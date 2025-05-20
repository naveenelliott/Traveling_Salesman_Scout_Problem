import pandas as pd
import os
import glob

folder_path = 'ASA_Raw_Data'

dfs = []
for file_path in glob.glob(os.path.join(folder_path, '*.csv')):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    if "uslc" in file_path.lower():
        df['League'] = 'USLC'
    elif "usl1" in file_path.lower():
        df['League'] = 'USL1'
    elif "mls" in file_path.lower():
        df['League'] = 'MLS'
    
    
    dfs.append(df)
    
asa_data = pd.concat(dfs, ignore_index=True)

asa_data.drop(columns=['Season', 'Dribbling', 'Fouling', 'Interrupting', 'Passing', 'Receiving',
       'Shooting', 'Unnamed: 0'], inplace=True)

asa_data['Goals Added p90'] = (asa_data['Goals Added']/asa_data['Minutes']) * 90



asa_data.to_csv('asa_data.csv', index=False)