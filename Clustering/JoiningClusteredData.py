import pandas as pd
import unicodedata
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

# -------------------- Load & Preprocess Data -------------------- #
def normalize_name(name):
    if not isinstance(name, str):
        return ''
    return unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('utf-8').lower()

# Load ASA data
asa_data = pd.read_csv('ASA_New_Raw_Data/asa_data_FINAL.csv')
asa_data = asa_data.drop(columns=['height_in', 'height_ft', 'weight_lb', 'minutes_played',
                                  'player_id', 'team_id'])
asa_data.drop_duplicates(subset='player_name', inplace=True)
asa_data.dropna(subset=['player_name'], inplace=True)
asa_data['player_name'] = asa_data['player_name'].apply(normalize_name)

asa_data['birth_date'] = pd.to_datetime(asa_data['birth_date'])
today = pd.Timestamp.today()
asa_data['Age'] = asa_data['birth_date'].apply(lambda bd: today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day)))

del asa_data['birth_date']

# Load and merge outfield players
fut_mls = pd.read_csv('Clustering/mls_players.csv')
fut_usl1 = pd.read_csv('Clustering/usl1_players.csv')
fut_uslc = pd.read_csv('Clustering/uslc_players.csv')
players = pd.concat([fut_mls, fut_usl1, fut_uslc], ignore_index=True)

# Clean player data
players = players.loc[:, ~players.columns.str.contains('penalty', case=False)]
players.drop(columns=['xGOT_percentile', 'xG_percentile', 'xA_percentile',
                      'Yellow cards_percentile', 'Red cards_percentile',
                      'Goals_percentile', 'Shots_percentile', 'Shots on target_percentile',
                      'Assists_percentile', 'Accurate passes_percentile', 'Pass accuracy_percentile',
                      'Touches_percentile'], inplace=True, errors='ignore')
players = players.fillna(0)
players.drop_duplicates(subset='name', inplace=True)
players['name'] = players['name'].apply(normalize_name)

# -------------------- Merge 1: Exact Name Match -------------------- #
merged_name = pd.merge(asa_data, players, left_on='player_name', right_on='name', how='inner')

# -------------------- Merge 2: player_code Matching -------------------- #
# Get unmatched
matched_names = set(merged_name['player_name'])
asa_remaining = asa_data[~asa_data['player_name'].isin(matched_names)].copy()
players_remaining = players[~players['name'].isin(matched_names)].copy()

# Generate player codes
def make_player_code(df, name_col='name'):
    df[['FirstName', 'LastName']] = df[name_col].str.strip().str.split(' ', n=1, expand=True)
    df['player_code'] = df['FirstName'].str[0].str.lower() + df['LastName'].str.lower()
    df['player_code'] += df.groupby('player_code').cumcount().where(
        df.groupby('player_code').cumcount() > 0, '').astype(str)
    return df.drop(columns=['FirstName', 'LastName'])

asa_remaining = make_player_code(asa_remaining, 'player_name')
players_remaining = make_player_code(players_remaining, 'name')

merged_code = pd.merge(asa_remaining, players_remaining, on='player_code', how='inner')

# -------------------- Merge 3: Manual Match -------------------- #
manual_names = ['evander', 'david pereira da costa', 'yeimar gomez andrade', 'yevhen cheberko', 'kalani kossa-rienzi', 'felipe', 
    'prince owusu', 'nouhou', 'shapi suleymanov', 'jasper loeffelsend', 'teenage hadebe', 'ralph priso', 'emiro garces',
    'rodrigo schlegel', 'maximiliano urruti', 'kaick', 'zanka', 'derrick etienne jr.', 'jeong sang-bin', 'alfredo midence alvarado', 
    'juan carlos obregon jr', 'louis herrera', 'kempes waldemar tekiela', 'ualefi', 'mikkel gøling', 
    'ronald alexis cerritos', 'aaron gomez', 'gabriel de freitas',
    'zahir vasquez', 'abel caputo', 'kwaku owusu', 'jose carlos anguiano',
    'damia viader i masdeu', 'hope avayevu', 'houssou landru', 'wilmer cabrera', 'gennaro michael nigro',
    'anton sojberg horup', 'jared trimmer', 'luiz fernando', 'jon-talen maples', 'roberto ydrach', 'harvey st. clair', 'bruno manuel rendon',
    'almir de jesus soto', 'speedy williams', 'dominick hernandez', 'dieng mamadou', 'guillermo diaz', 'paul gindiri', 
    'juan sebastian herrera', 'preston tabort etaka', 'alasanne ates diouf', 'abdul illal osumanu', 'lucas melano', 'adewale obalola']

manual_players = players_remaining[~players_remaining['name'].isin(merged_code['name'])]
manual_players = manual_players.reset_index(drop=True)
manual_players['name'] = manual_names

merged_manual = pd.merge(asa_remaining, manual_players, left_on='player_name', right_on='name', how='inner')

# -------------------- Final Assembly -------------------- #
all_merged = pd.concat([merged_name, merged_code, merged_manual], ignore_index=True)

matched_names = set(all_merged['name'])
manual_players = manual_players[~manual_players['name'].isin(matched_names)].copy()

# Drop helper columns
all_merged.drop(columns=['FirstName', 'LastName'], errors='ignore', inplace=True)

# Optionally clean up 'name' (from player table) if no longer needed
all_merged.drop(columns=['player_code_x', 'player_code_y', 'name', 'player_code'], errors='ignore', inplace=True)

all_merged = all_merged.loc[:, ~all_merged.columns.str.contains('penalties', case=False)]

le = LabelEncoder()
all_merged['general_position'] = le.fit_transform(all_merged['general_position'])

for i, class_label in enumerate(le.classes_):
    print(f"{i} → {class_label}")

all_merged.to_csv('Clustering/final_joined.csv', index=False)

gk_1 = pd.read_csv('Clustering/mls_gks.csv')

gk_2 = pd.read_csv('Clustering/usl1_gks.csv')

gk_3 = pd.read_csv('Clustering/uslc_gks.csv')

total_gks = pd.concat([gk_1, gk_2, gk_3], ignore_index=True)

total_gks = total_gks.loc[:, ~total_gks.columns.str.contains('penalty', case=False)]

total_gks.to_csv('Clustering/final_joined_gk.csv', index=False)
