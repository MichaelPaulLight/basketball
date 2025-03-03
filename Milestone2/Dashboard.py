import dash

from dash import dcc
from dash import html
import asyncio
import aiohttp
import pandas as pd
import base64
import pkg_resources
from sklearn.preprocessing import StandardScaler
from scipy.spatial.distance import cdist
import plotly.express as px

# Print the versions of the packages used
print(f"dash version: {pkg_resources.get_distribution('dash').version}")
print(f"pandas version: {pkg_resources.get_distribution('pandas').version}")
print(f"plotly version: {pkg_resources.get_distribution('plotly').version}")
print(f"aiohttp version: {pkg_resources.get_distribution('aiohttp').version}")
print(f"pyarrow version: {pkg_resources.get_distribution('pyarrow').version}")

# Load the data
df = pd.read_parquet("data/21-25player_clusters.parquet")

def player_info(seasons):
    
    headers = {'Connection': 'keep-alive',
            'Host': 'stats.nba.com',
            'Origin': 'http://stats.nba.com',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://stats.nba.com',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true',
            'Accept-Language': 'en-US,en;q=0.5',
            "Accept": "application/json, text/plain, */*",
            "X-NewRelic-ID": "VQECWF5UChAHUlNTBwgBVw==",
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) " + \
                            "AppleWebKit/537.36 (KHTML, like Gecko) " + \
                            "Chrome/84.0.4147.89 Safari/537.36"}


    async def fetch_play_by_play(session, season):
        url = f"https://stats.nba.com/stats/playerindex?Active=&AllStar=&College=&Country=&DraftPick=&DraftRound=&DraftYear=&Height=&Historical=&LeagueID=00&Season={season}&TeamID=0&Weight="
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                df =  pd.DataFrame(data['resultSets'][0]['rowSet'], columns=data['resultSets'][0]['headers'])
                return df
            else:
                print(f"Error fetching play-by-play data for game {season} from {url}: {response.status}")
                return pd.DataFrame()

    async def main():
        async with aiohttp.ClientSession() as session:
            total_data = pd.DataFrame()
            for season in seasons:
                player_data = await fetch_play_by_play(session, season)
                total_data = pd.concat([player_data])
            # Concatenate all play-by-play data into a single DataFrame
            return total_data
            

            

    # Run the main function
    result = asyncio.run(main())
    return result
player_info_df = player_info(df['SEASON'].unique())
# Merge the player_info_df with the original df to get the positions
df = df.merge(player_info_df[['PERSON_ID', 'POSITION']], left_on='PLAYER_ID', right_on='PERSON_ID', how='left')

# Create the 'positions' column
df['positions'] = df['POSITION']

# Initialize the Dash app
app = dash.Dash(__name__)

image_filename = '21-25data.png'  # Replace with your image file
encoded_image = base64.b64encode(open(image_filename, 'rb').read()).decode()

# Define the layout
app.layout = html.Div(children=[
    html.H1(children='Cluster Position Distribution'),

    html.Img(
        id='heatmap',
        src=f'data:image/png;base64,{encoded_image}',
        style={'width': '800px'}  # Adjust the width to match the bar graph
    ),

    dcc.Dropdown(
        id='cluster-dropdown',
        options=[{'label': str(cluster), 'value': cluster} for cluster in df['Cluster_Labels'].unique()],
        value=df['Cluster_Labels'].unique()[0]
    ),
    dcc.Graph(
        id='bar-graph'
    ),
    dcc.Input(
        id='player-name-input',
        type='search',
        placeholder='Enter player name'
    ),
    html.Button('Search', id='search-button', n_clicks=0),

    html.Table(id='similar-players-table'),
])

# Define the callback to update the bar graph based on the selected cluster
@app.callback(
    dash.dependencies.Output('bar-graph', 'figure'),
    [dash.dependencies.Input('cluster-dropdown', 'value')]
)
def update_bar_graph(selected_cluster):
    filtered_df = df[df['Cluster_Labels'] == selected_cluster]
    
    # Bar graph
    position_counts = filtered_df['positions'].value_counts(normalize=True) * 100
    bar_fig = px.bar(position_counts, x=position_counts.index, y=position_counts.values, labels={'x': 'Position', 'y': 'Percentage'}, title=f'Position Distribution for Cluster {selected_cluster}')
    
    # Update the layout to make the bar graph thinner
    bar_fig.update_layout(
        width=400,  # Adjust the width as needed
        height=600  # Adjust the height as needed
    )
    
    return bar_fig

# Define the callback to update the table based on the player name input
@app.callback(
    dash.dependencies.Output('similar-players-table', 'children'),
    [dash.dependencies.Input('search-button', 'n_clicks')],
    [dash.dependencies.State('player-name-input', 'value')]
)
def update_similar_players_table(n_clicks, player_name):
    if n_clicks is None or player_name is None:
        return []

    season = '2024-25'

    player_data = df[(df['player_name'] == player_name) & (df['SEASON'] == season)]
    if player_data.empty:
        print(f"Player {player_name} not found in the {season} season.")
        return [html.Tr([html.Td(f"Player {player_name} not found in the {season} season.")])]
    else:
        player_cluster = player_data['Cluster_Labels'].values[0]
        print(f"Player: {player_name}, Season: {season}, Cluster: {player_cluster}")

        # Calculate cosine similarity
        player_vector = player_data[['AVG_2_DIST', 'AVG_3_DIST', 'FG2_PCT', 'FG3_PCT','DREB','STL','BLK','PF','FG2Target','FG3Target']].values
        all_vectors = df[['AVG_2_DIST', 'AVG_3_DEF_DIST', 'FG2_PCT', 'FG3_PCT', 'DREB','STL','BLK','PF','FG2Target','FG3Target']].values
        # Get the indices of the top 3 most similar players
        scaler = StandardScaler()
        all_vectors = scaler.fit_transform(all_vectors)
        player_vector = scaler.transform(player_vector)

        similarities = cdist(player_vector, all_vectors, metric='euclidean').flatten()
        similar_indices = similarities.argsort()[:4]

        similar_players = df.iloc[similar_indices][['player_name', 'SEASON', 'Cluster_Labels','FG2_PCT','FG2Target', 'FG3_PCT','FG3Target','DREB','STL','BLK','PF']]
        # Format the 'FG2_PCT', 'FG2Target', 'FG3_PCT', 'FG3Target' columns as percentages
        similar_players['FG2_PCT'] = similar_players['FG2_PCT'].apply(lambda x: f"{x:.2%}")
        similar_players['FG2Target'] = similar_players['FG2Target'].apply(lambda x: f"{x:.2%}")
        similar_players['FG3_PCT'] = similar_players['FG3_PCT'].apply(lambda x: f"{x:.2%}")
        similar_players['FG3Target'] = similar_players['FG3Target'].apply(lambda x: f"{x:.2%}")
        table_header = [
            html.Thead(html.Tr([html.Th(col) for col in similar_players.columns]))
        ]
        table_body = [
            html.Tbody([html.Tr([html.Td(similar_players.iloc[i][col]) for col in similar_players.columns]) for i in range(len(similar_players))])
        ]
        return table_header + table_body
    # Create the table rows


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)