import pandas as pd
import pyarrow as pa

import pyarrow.parquet as pq

# Read Parquet file into DataFrame
def process_defender_dashboard(df):
    dist_map = {'0-2 Feet - Very Tight': 1, '2-4 Feet - Tight': 3, '4-6 Feet - Open': 5, '6+ Feet - Wide Open': 7}

    df['CLOSE_DEF_DIST_RANGE'] = df['CLOSE_DEF_DIST_RANGE'].map(dist_map).astype(int)
    df['FG2M'] = df['FG2M'].astype(int)
    df['FG2A'] = df['FG2A'].astype(int) 
    df['FG3M'] = df['FG3M'].astype(int)
    df['FG3A'] = df['FG3A'].astype(int)
    df['GP'] = df['GP'].astype(int)
    df['G'] = df['G'].astype(int)

    df['TOT_DIST_2'] = df['CLOSE_DEF_DIST_RANGE'] * df['FG2A']
    df['TOT_DIST_3'] = df['CLOSE_DEF_DIST_RANGE'] * df['FG3A']

    # Sum columns based on PLAYER_ID
    agg_df = df.groupby(['PLAYER_ID']).agg({
        'FG2M': 'sum',
        'FG2A': 'sum',
        'FG3M': 'sum',
        'FG3A': 'sum',
        'TOT_DIST_2': 'sum',
        'TOT_DIST_3': 'sum'
    }).reset_index()

    agg_df['AVG_2_DEF_DIST'] = agg_df['TOT_DIST_2'] / agg_df['FG2A']
    agg_df['AVG_3_DEF_DIST'] = agg_df['TOT_DIST_3'] / agg_df['FG3A']
    agg_df['FG2_PCT'] = agg_df['FG2M'] / agg_df['FG2A']
    agg_df['FG3_PCT'] = agg_df['FG3M'] / agg_df['FG3A']
    agg_df['FG_Split'] = agg_df['FG3A'] / agg_df['FG2A']
    agg_df['FGA'] = agg_df['FG2A'] + agg_df['FG3A']
    
    return agg_df


df = pd.read_parquet('data/20250220defender_dashboard.parquet')
agg_df = process_defender_dashboard(df)

def process_play_by_play(df):
    # Split 'lineup_home' and 'lineup_away' into 5 separate columns
    df[['home_player1', 'home_player2', 'home_player3', 'home_player4', 'home_player5']] = df['lineup_home'].str.split(', ', expand=True)
    df[['away_player1', 'away_player2', 'away_player3', 'away_player4', 'away_player5']] = df['lineup_away'].str.split(', ', expand=True)
    df['2pta'] = (df['desc_value'] == 2).astype(int)
    df['3pta'] = (df['desc_value'] == 3).astype(int)
    df['2ptm'] = (df['shot_pts'] == 2).astype(int)
    df['3ptm'] = (df['shot_pts'] == 3).astype(int)

    # Split into separate DataFrames based on the values in the 'possession' column
    home_possession_df = df[df['poss_home'] == 1]
    away_possession_df = df[df['poss_away'] == 1]

    agg_dfs = []

    for i in range(1, 6):
        away_agg_df = away_possession_df.groupby(f'home_player{i}').agg({
            'poss_home': 'count',
            '2pta': 'sum',
            '2ptm': 'sum',
            '3pta': 'sum',
            '3ptm': 'sum'
        }).reset_index().rename(columns={
            f'home_player{i}': 'player_name',
            'poss_home': 'total_possessions',
            '2pta': 'total_2pta',
            '2ptm': 'total_2ptm',
            '3pta': 'total_3pta',
            '3ptm': 'total_3ptm'
        })
        
        home_agg_df = home_possession_df.groupby(f'away_player{i}').agg({
            'poss_away': 'count',
            '2pta': 'sum',
            '2ptm': 'sum',
            '3pta': 'sum',
            '3ptm': 'sum'
        }).reset_index().rename(columns={
            f'away_player{i}': 'player_name',
            'poss_away': 'total_possessions',
            '2pta': 'total_2pta',
            '2ptm': 'total_2ptm',
            '3pta': 'total_3pta',
            '3ptm': 'total_3ptm'
        })
        
        combined_agg_df = pd.concat([away_agg_df, home_agg_df], ignore_index=True)
        agg_dfs.append(combined_agg_df)

    final_agg_df = pd.concat(agg_dfs).groupby('player_name').sum().reset_index()
    final_agg_df = final_agg_df[final_agg_df['total_possessions'] >= 1000]

    return final_agg_df

#Example usage
pbp_df = pd.read_parquet('data/20250220_combined_pbp.parquet')
final_agg_df = process_play_by_play(pbp_df)


def filter_player_stats(df):
    return df[['PLAYER_ID', 'DREB', 'STL', 'BLK', 'PF', 'SEASON','GP']]

player_stats_df = pd.read_parquet('data/2024-25player_per100poss.parquet')
filtered_df = filter_player_stats(player_stats_df)

player_info_df = pd.read_parquet('data/2024-25player_info.parquet')
filtered_player_info_df = player_info_df[['PERSON_ID', 'DISPLAY_LAST_COMMA_FIRST', 'DISPLAY_FIRST_LAST']]
filtered_player_info_df['PERSON_ID'] = filtered_player_info_df['PERSON_ID'].astype(int)
agg_df['PLAYER_ID'] = agg_df['PLAYER_ID'].astype(int)
merged_df = agg_df.merge(filtered_player_info_df, left_on='PLAYER_ID', right_on='PERSON_ID', how='left')
merged_df = merged_df.merge(final_agg_df, left_on='DISPLAY_FIRST_LAST', right_on='player_name', how='left')
merged_df = merged_df.merge(filtered_df, on='PLAYER_ID', how='left')
merged_df['FG2Target'] = merged_df['FG2A']/merged_df['total_2pta']
merged_df['FG3Target'] = merged_df['FG3A']/merged_df['total_3pta']
merged_df['FGTaget'] = merged_df['FGA']/merged_df['total_possessions']
merged_df['2FG%diff'] = merged_df['FG2_PCT'] - (merged_df['total_2ptm']/merged_df['total_2pta'])
merged_df['3FG%diff'] = merged_df['FG3_PCT'] - (merged_df['total_3ptm']/merged_df['total_3pta'])
merged_df['Poss/Game'] = merged_df['total_possessions']/merged_df['GP']
merged_df.drop(columns = ['FG2M','FG2A','FG3M','FG3A','total_possessions','GP','FGA','TOT_DIST_2', 'TOT_DIST_3', 'total_2pta','total_2ptm','total_3ptm','total_3pta','DISPLAY_FIRST_LAST','PERSON_ID','DISPLAY_LAST_COMMA_FIRST'], inplace=True)
merged_df.dropna(inplace=True)
# Reorder columns
cols = ['player_name', 'SEASON', 'PLAYER_ID'] + [col for col in merged_df.columns if col not in ['player_name', 'SEASON', 'PLAYER_ID']]
merged_df = merged_df[cols]

pd.set_option('display.max_columns', None)

# Display summary of the DataFrame
print(merged_df.describe(include='all'))
print(merged_df.head(10))
# Save the merged DataFrame as a Parquet file
merged_df.to_parquet('data/24-25merged_player_stats.parquet', index=False)