import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering
from yellowbrick.cluster import KElbowVisualizer 
from scipy.stats import zscore

pd.set_option('display.max_columns', None)

def plot_dendrogram(model, **kwargs):
    n_samples = len(model.labels_)
    counts = np.zeros(model.children_.shape[0])
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if (child_idx < n_samples):
                current_count += 1
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)
    
    # Plot the dendrogram
    dendrogram(linkage_matrix, **kwargs)
    
    
    # Add cluster labels
    if 'labels' in kwargs:
        for i, d in zip(kwargs['labels'], linkage_matrix):
            plt.text(d[0], d[1], str(i), ha='center', va='bottom')



if __name__ == '__main__':
#import argparse 
    #Used originally alongside makefile, commented out for now
    #parser = argparse.ArgumentParser()
    #parser.add_argument('input', help='input file')
    #args = parser.parse_args()
    df0 = pd.read_parquet('data/21_22merged_player_stats.parquet')
    df0['SEASON'] = '2021-22'
    df1 = pd.read_parquet('data/22_23merged_player_stats.parquet')
    df1['SEASON'] = '2022-23'
    df2 = pd.read_parquet('data/23_24merged_player_stats.parquet')
    df2['SEASON'] = '2023-24'
    df3 = pd.read_parquet('data/24_25merged_player_stats.parquet')
    df3['SEASON'] = '2024-25'
    df = pd.concat([df0, df1, df2, df3])
    #Players who did not have a high enough 3pt attempt rate were given the average 3pt percentage
    avg_fg3_pct = df['FG3_PCT'].mean()
    df.loc[df['FG3Target'] < 0.025, 'FG3_PCT'] = avg_fg3_pct
    df.loc[df['FG3_PCT']== 0, 'FG3_PCT'] = avg_fg3_pct
    #A Player's arm length is estimated using half of (their wingspan - .25 of their height without shoes ~ chest length)
    df['AVG_2_DIST'] = df['AVG_2_DEF_DIST'] - ((df['WINGSPAN']-(df['HEIGHT_WO_SHOES']/48))/24)
    df['AVG_3_DIST'] = df['AVG_3_DEF_DIST'] - ((df['WINGSPAN']-(df['HEIGHT_WO_SHOES']/48))/24)
    X = df[['FG2Target','FG2_PCT','AVG_2_DIST', 'FG3Target','FG3_PCT','AVG_3_DIST',  'DREB','BLK','PF','STL',]]
    #Scale the data
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    best_n_clusters = 0
    best_silhouette_score = -1
    best_fit_X = None
    distortions = []

    #Uncomment the following lines to produce the elbow plot
    # model = AgglomerativeClustering(linkage='ward',compute_distances=True)
    # visualizer = KElbowVisualizer(model, k=(2,20), timings=False)
    # visualizer.fit(X)
    # visualizer.show(outpath="elbow.png")

    model_best = AgglomerativeClustering(linkage='ward',n_clusters=9, compute_distances=True)
    print(model_best.get_params())
    model_best.fit(X)
    
    # Cluster Dendrogram - currently set to show the top 4 levels of cluster merging
    plt.figure(figsize=(10, 8))
    plt.title("Hierarchical Clustering Dendrogram")
    plot_dendrogram(model_best, truncate_mode="level", p=4, orientation='left')
    plt.xlabel("Number of points in node (or index of point if no parenthesis).")
    plt.axvline(x=20, color='black', linestyle='--', label='threshold')
    plt.legend(loc='upper left')
    plt.show()

    fit_X = model_best.fit_predict(X)
    X_df = pd.DataFrame(X, columns=['FG2Target','FG2_PCT','AVG_2_DIST', 'FG3Target','FG3_PCT','AVG_3_DIST',  'DREB','BLK','PF','STL',])
    X_df[['AVG_2_DIST', 'AVG_3_DIST', 'FG2_PCT', 'FG3_PCT', 'PF','FG2Target','FG3Target']] = -1*X_df[['AVG_2_DIST', 'AVG_3_DIST', 'FG2_PCT', 'FG3_PCT', 'PF','FG2Target','FG3Target']]
    X_df['Cluster_Labels'] = fit_X
    df['Cluster_Labels'] = fit_X

    #Rename cluster for context
    cluster_dict = {0: '1. Perimeter Help',1: '3. Perimeter On-Ball',
                    2: '5. Interior Float',3: '9. Pickpockets',
                    4:'7. Interior Help', 5: '2. Perimeter Only',
                    6:'6. Interior Paint',7:'4. Interior Risk Averse',
                    8:'8. Interior Close Out'}
    df['Cluster_Labels'] = df['Cluster_Labels'].map(cluster_dict)
    X_df['Cluster_Labels'] = X_df['Cluster_Labels'].map(cluster_dict)
    cluster_counts = df['Cluster_Labels'].value_counts()
    print("Cluster counts:")
    print(cluster_counts)
    #df.to_parquet('data/21-25player_clusters.parquet', index=False)
    cluster_averages = X_df.groupby('Cluster_Labels').mean()
    print(cluster_averages)

    sns.clustermap(cluster_averages, z_score=1, cmap = 'vlag', row_cluster=False, col_cluster=False)
    plt.savefig('21-25data.png', dpi=300)
    plt.show()

    player_name = input("Enter player's name (default: LeBron James): ") or "LeBron James"
    season = input("Enter season (default: 2024-25): ") or "2024-25"

    if 'player_name' not in df.columns:
        raise KeyError("The column 'player_name' does not exist in the DataFrame.")
    player_data = df[(df['player_name'] == player_name) & (df['SEASON'] == season)]
    if player_data.empty:
        print(f"Player {player_name} not found in the {season} season.")
    else:
        player_cluster = player_data['Cluster_Labels'].values[0]
        print(f"Player: {player_name}, Season: {season}, Cluster: {player_cluster}")

        # Calculate cosine similarity
        player_vector = player_data[['FG2Target','FG2_PCT','AVG_2_DIST', 'FG3Target','FG3_PCT','AVG_3_DIST','DREB','BLK','PF','STL']].values
        all_vectors = df[['FG2Target','FG2_PCT','AVG_2_DIST', 'FG3Target','FG3_PCT','AVG_3_DIST' ,'DREB','BLK','PF','STL']].values
        scaler.fit(all_vectors)  # Fit the scaler with all_vectors
        player_vector = scaler.transform(player_vector)
        all_vectors = scaler.transform(all_vectors)
        similarities = cosine_similarity(player_vector, all_vectors).flatten()

        # Get the indices of the top 3 most similar players
        similar_indices = [i for i in similarities.argsort()[-4:-1][::-1] if i < len(df)]
        print(similar_indices)
        print(len(df))
        similar_players = df.iloc[similar_indices][['player_name', 'SEASON', 'Cluster_Labels']]
        print("Three most similar players:")
        for _, row in similar_players.iterrows():
            print(f"Player: {row['player_name']}, Season: {row['SEASON']}, Cluster: {row['Cluster_Labels']}")

    # # Find players with the lowest 'AVG_3_DEF_DIST'
    # # Print samples of every cluster with all columns
    # for cluster_label in df['Cluster_Labels'].unique():
    #     print(f"\nCluster {cluster_label} samples:")
    #     cluster_samples = df[(df['Cluster_Labels'] == cluster_label) & (df['SEASON'] == season)].sample(n=5, random_state=42)
    #     print(cluster_samples)