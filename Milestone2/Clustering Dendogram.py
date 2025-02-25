import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering



def plot_dendrogram(model, **kwargs):
    n_samples = len(model.labels_)
    counts = np.zeros(model.children_.shape[0])
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1 
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)



if __name__ == '__main__':
#import argparse 
    import pandas as pd
    import seaborn as sns
    from sklearn.metrics import silhouette_score
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import StandardScaler
    #parser = argparse.ArgumentParser()
    #parser.add_argument('input', help='input file')
    #args = parser.parse_args()
    df1 = pd.read_parquet('data/22_23merged_player_stats.parquet')
    df2 = pd.read_parquet('data/23_24merged_player_stats.parquet')
    df3 = pd.read_parquet('data/24_25merged_player_stats.parquet')
    df = pd.concat([df1, df2, df3])
    X = df[['AVG_2_DEF_DIST', 'AVG_3_DEF_DIST', 'FG2_PCT', 'FG3_PCT', 'FG_Split', 'DREB','STL','BLK','PF','FG2Target','FG3Target','FGTaget','2FG%diff','3FG%diff','Poss/Game']]
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    best_n_clusters = 0
    best_silhouette_score = -1
    best_fit_X = None

    for n_clusters in range(8, 16):
        model = AgglomerativeClustering(n_clusters=n_clusters,metric='cosine', linkage='single',compute_distances=True)
        fit_X = model.fit_predict(X)
        score = silhouette_score(X, fit_X)
        if score > best_silhouette_score:
            best_silhouette_score = score
            best_n_clusters = n_clusters
            best_fit_X = fit_X

    print(f"Best number of clusters: {best_n_clusters}")
    print(f"Best silhouette score: {best_silhouette_score}")
    fit_X = best_fit_X
    X_df = pd.DataFrame(X, columns=['AVG_2_DEF_DIST', 'AVG_3_DEF_DIST', 'FG2_PCT', 'FG3_PCT', 'FG_Split', 'DREB','STL','BLK','PF','FG2Target','FG3Target','FGTaget','2FG%diff','3FG%diff','Poss/Game'])
    X_df['Cluster_Labels'] = fit_X
    df['Cluster_Labels'] = fit_X
    cluster_averages = X_df.groupby('Cluster_Labels').mean()
    print(cluster_averages)
    #plt.title("Hierarchical Clustering Dendrogram")
    # plot the top three levels of the dendrogram
    #plot_dendrogram(model, truncate_mode="level", p=3)
    #plt.xlabel("Number of points in node (or index of point if no parenthesis).")
    sns.clustermap(cluster_averages, z_score=1)
    plt.savefig('22-23data.png', dpi=300)
    plt.show()

    player_name = input("Enter player's name (default: LeBron James): ") or "LeBron James"
    season = '2024-25'

    player_data = df[(df['player_name'] == player_name) & (df['SEASON'] == season)]
    if player_data.empty:
        print(f"Player {player_name} not found in the {season} season.")
    else:
        player_cluster = player_data['Cluster_Labels'].values[0]
        print(f"Player: {player_name}, Season: {season}, Cluster: {player_cluster}")

        # Calculate cosine similarity
        player_vector = player_data[['AVG_2_DEF_DIST', 'AVG_3_DEF_DIST', 'FG2_PCT', 'FG3_PCT', 'FG_Split', 'DREB','STL','BLK','PF','FG2Target','FG3Target','FGTaget','2FG%diff','3FG%diff','Poss/Game']].values
        all_vectors = df[['AVG_2_DEF_DIST', 'AVG_3_DEF_DIST', 'FG2_PCT', 'FG3_PCT', 'FG_Split', 'DREB','STL','BLK','PF','FG2Target','FG3Target','FGTaget','2FG%diff','3FG%diff','Poss/Game']].values
        player_vector = scaler.transform(player_vector)
        all_vectors = scaler.transform(all_vectors)
        similarities = cosine_similarity(player_vector, all_vectors).flatten()

        # Get the indices of the top 3 most similar players
        similar_indices = similarities.argsort()[-4:-1][::-1]  # Exclude the player itself

        similar_players = df.iloc[similar_indices][['player_name', 'SEASON', 'Cluster_Labels']]
        print("Three most similar players:")
        for _, row in similar_players.iterrows():
            print(f"Player: {row['player_name']}, Season: {row['SEASON']}, Cluster: {row['Cluster_Labels']}")