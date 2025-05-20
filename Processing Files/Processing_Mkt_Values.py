import pandas as pd
import os
import glob
import re


folder_path = 'Market_Values_Raw_Data'

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
    
mkt_values = pd.concat(dfs, ignore_index=True)

mkt_values['market_value'] = mkt_values['market_value'].str.replace('-', '0')

# Extract team name from URL
def extract_team_name(url):
    match = re.search(r'transfermarkt\.us/([^/]+)/', url)
    if match:
        return match.group(1).replace('-', ' ').title()
    return None

mkt_values['Team'] = mkt_values['team_url'].apply(extract_team_name)

def parse_market_value(val):
    if val == '0' or pd.isna(val):
        return 0.0
    val = val.replace('€', '').lower().strip()
    if val.endswith('m'):
        return float(val[:-1]) * 1_000_000
    elif val.endswith('k'):
        return float(val[:-1]) * 1_000
    else:
        try:
            return float(val)
        except ValueError:
            return None

mkt_values['market_value'] = mkt_values['market_value'].apply(parse_market_value)

del mkt_values['player_link'], mkt_values['team_url']

mkt_values.to_csv('transfermarkt_data_processed.csv', index=False)