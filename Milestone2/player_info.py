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
        url = f"https://stats.nba.com/stats/draftcombineplayeranthro?LeagueID=00&SeasonYear={season}"
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                df =  pd.DataFrame(data['resultSets'][0]['rowSet'], columns=data['resultSets'][0]['headers'])
                print(f"Processed game {season} with {len(df)} rows")
                return df
            else:
                print(f"Error fetching play-by-play data for game {season} from {url}: {response.status}")
                return pd.DataFrame()

    async def main():
        async with aiohttp.ClientSession() as session:
            total_player_data = pd.DataFrame()
            for season in seasons:
                player_data = await fetch_play_by_play(session, season)
                total_player_data = pd.concat([total_player_data, player_data], ignore_index=True)
            # Concatenate all play-by-play data into a single DataFrame
            return total_player_data
            
            
            # Save to a parquet file
            

    # Run the main function
    result = asyncio.run(main())
    return result

if __name__ == '__main__':
    import asyncio
    import aiohttp
    import pandas as pd
    from nba_api.stats.endpoints import leaguegamefinder
    import os
    import pyarrow.parquet as pq
    import pyarrow as pa
    seasons = list(range(2000, 2025))
    player_data = player_info(seasons)
    print(player_data.head(10))
    pq.write_table(pa.Table.from_pandas(player_data), '00_24_anthro.parquet')
    
    
    