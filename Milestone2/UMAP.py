import numpy as np
import pandas as pd
from sklearn.decomposition import KernelPCA
from sklearn.preprocessing import StandardScaler
import umap
import matplotlib.pyplot as plt

cluster_DF = pd.read_parquet('data/21-25player_clusters.parquet')
X = cluster_DF[['FG2Target','FG2_PCT','AVG_2_DIST', 'FG3Target','FG3_PCT','AVG_3_DIST', 'DREB','BLK','PF','STL',]]
scaler = StandardScaler()
X = scaler.fit_transform(X)
reducer = umap.UMAP(n_components=2)
transformed_data = reducer.fit_transform(X)
cluster_DF['UMAP1'] = transformed_data[:, 0]
cluster_DF['UMAP2'] = transformed_data[:, 1]
cluster_dict = {'1. Perimeter Help': 1, '3. Perimeter On-Ball': 3,
                '5. Interior Float': 5 ,'9. Pickpockets': 9,
                '7. Interior Help': 7, '2. Perimeter Only': 2,
                '6. Interior Paint': 6, '4. Interior Risk Averse':4,
                '8. Interior Close Out': 8}
cluster_DF['Cluster'] = cluster_DF['Cluster_Labels'].map(cluster_dict)
plt.figure(figsize=(10, 7))
#colors = {1: 'red', 2: 'blue', 3: 'green', 4: 'purple', 5: 'orange', 6: 'brown', 7: 'pink', 8: 'gray', 9: 'cyan'}
colors2 = {1: 'red', 2: 'red', 3: 'red', 4: 'red', 5: 'green', 6: 'green', 7: 'green', 8: 'green', 9: 'green'}
scatter = plt.scatter(cluster_DF['UMAP1'], cluster_DF['UMAP2'], c=cluster_DF['Cluster'].map(colors2))
handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=label) 
           for label, color in colors2.items()]
plt.legend(title='Cluster', handles=handles)
plt.xlabel('UMAP 1')
plt.ylabel('UMAP 2')
plt.title('UMAP Two Branches')
plt.savefig('UMAP2.png')
plt.show()
