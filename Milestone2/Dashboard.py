import dash
from dash import dcc
from dash import html
import pandas as pd
import requests
import base64
import io

import plotly.express as px

# Load the data
df = pd.read_parquet("data/22-25player_clusters.parquet")

def player_info(seasons):
    import asyncio
    import aiohttp
    import pandas as pd
    from nba_api.stats.endpoints import leaguegamefinder
    import os
    

    # Get all games for the season
    

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
            
            
            # Save to a parquet file
            

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

image_filename = '22-25data.png'  # Replace with your image file
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

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)