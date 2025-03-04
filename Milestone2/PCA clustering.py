import numpy as np
import pandas as pd
from sklearn.decomposition import KernelPCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

df = pd.read_parquet('data/21-25player_clusters.parquet')
X = df[['FG2Target','FG2_PCT','AVG_2_DIST', 'FG3Target','FG3_PCT','AVG_3_DIST', 'DREB','BLK','PF','STL',]]
scaler = StandardScaler()
X = scaler.fit_transform(X)
pca = KernelPCA(n_components=2, kernel='sigmoid')
transformed_data = pca.fit_transform(X)
df['PCA1'] = transformed_data[:, 0]
df['PCA2'] = transformed_data[:, 1]
cluster_dict = {'1. Perimeter Secondary Option': 1, '3. The Marks': 3,
                '5. Enforcers/Inside Help': 5 ,'9. Pickpockets': 9,
                '7. Perimeter and Inside Help': 7, '2. Perimeter Bad Defenders': 2,
                '6. True Rim Protectors': 6, '4. Risk Averse Paint Defender': 4,
                '8. Anchors who Close Out': 8}
df['Cluster'] = df['Cluster_Labels'].map(cluster_dict)
plt.figure(figsize=(10, 7))
colors = {1: 'red', 2: 'blue', 3: 'green', 4: 'purple', 5: 'orange', 6: 'brown', 7: 'pink', 8: 'gray', 9: 'cyan'}
#colors2 = {1: 'red', 2: 'red', 3: 'red', 4: 'red', 5: 'green', 6: 'green', 7: 'green', 8: 'green', 9: 'green'}
scatter = plt.scatter(df['PCA1'], df['PCA2'], c=df['Cluster'].map(colors))
handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10, label=label) 
           for label, color in colors.items()]
plt.legend(title='Cluster', handles=handles)
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.title('PCA Clustering')
plt.savefig('PCA_Clustering2.png')
plt.show()

print(pca.explained_variance_ratio_)