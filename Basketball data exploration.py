import pandas as pd
pd.set_option('display.max_columns', 1000)

# Path to the parquet file
file_path = r"C:\Users\adabi\OneDrive\Documents\Basketball - Milestone 2\data\250203_pbp_gt.parquet"
file_path2 = r"C:\Users\adabi\OneDrive\Documents\Basketball - Milestone 2\data\new_pbp_2025-02-15.parquet"

# Read the parquet file
df = pd.read_parquet(file_path)
df2 = pd.read_parquet(file_path2)
#print(df.columns)
print(df2.columns)  
# Get a summary of the columns
summary = df.describe(include='all')
summary2 = df2.describe(include='all')


"""# Extract relevant columns
home_lineups = df2.iloc[:, [22, 15, 27, 28]]
away_lineups = df2.iloc[:, [23, 16, 28, 27]]

# Rename columns for clarity
home_lineups.columns = ['Lineup', 'Team', 'Points_For','Points_Against']
away_lineups.columns = ['Lineup', 'Team', 'Points_For','Points_Against']
#print(home_lineups.head(10))    
# Calculate total points for home lineups
home_points = home_lineups.groupby(['Team', 'Lineup']).agg({'Points_For': 'sum','Points_Against':'sum'}).reset_index()

# Calculate total points against for away lineups
away_points = away_lineups.groupby(['Team', 'Lineup']).agg({'Points_For':'sum','Points_Against': 'sum'}).reset_index()

# Merge the home and away points
total_points = pd.concat([home_points, away_points], axis=0).groupby(['Team', 'Lineup']).sum().reset_index()

# Find the 10 most common lineups for each team
most_common_lineups = total_points.groupby('Team').apply(lambda x: x.nlargest(10, 'Points_For')).reset_index(drop=True)
most_common_lineups['Net_Points'] = most_common_lineups['Points_For'] - most_common_lineups['Points_Against']
# Print the result
print(most_common_lineups.head(10))"""