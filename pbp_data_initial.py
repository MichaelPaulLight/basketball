def pbp_raw(game_ids):
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


    async def fetch_play_by_play(session, game_id):
        url = f"https://stats.nba.com/stats/playbyplayv2?GameID={game_id}&StartPeriod=0&EndPeriod=14"
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                df =  pd.DataFrame(data['resultSets'][0]['rowSet'], columns=data['resultSets'][0]['headers'])
                print(f"Processed game {game_id} with {len(df)} rows")
                return df
            else:
                print(f"Error fetching play-by-play data for game {game_id} from {url}: {response.status}")
                return pd.DataFrame()

    async def main():
        async with aiohttp.ClientSession() as session:
            play_by_play_data = []
            for i, game_id in enumerate(game_ids):
                play_by_play_data.append(await fetch_play_by_play(session, game_id))
                #print(len(play_by_play_data))
                if (i + 1) % 252 == 0:
                    print(f"Processed {i + 1} games, waiting for 60 seconds...")
                    await asyncio.sleep(60)
            
            # Concatenate all play-by-play data into a single DataFrame
            complete_data = pd.concat(play_by_play_data,ignore_index=True)
            print(len(complete_data))
            return complete_data
            
            
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

    gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable='2024-25', 
                                                league_id_nullable='00', 
                                                season_type_nullable='Regular Season')
    games = gamefinder.get_data_frames()[0]

    existing_game_ids = set()
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", default="data/250203_pbp_gt.parquet")
    parser.add_argument("output_file",default="data/new_pbp.parquet")
    args = parser.parse_args()
    parquet_file = args.input_file

    if os.path.exists(parquet_file):
        existing_data = pq.read_table(parquet_file).to_pandas()
        #print(existing_data.columns)
        existing_game_ids = list(map(int,existing_data['game_id'].unique()))
        existing_game_ids = ["00"+str(game_id) for game_id in existing_game_ids]
        #print(existing_game_ids[:5])
    #print(games['GAME_ID'].unique())
    new_game_ids = [game_id for game_id in games['GAME_ID'].unique() if game_id not in existing_game_ids]
    #print(new_game_ids[:5])
    #print(existing_game_ids[:5])
    #print(len(new_game_ids))
    new_game_data = pbp_raw(new_game_ids)
    new_game_data.columns = new_game_data.columns.str.lower()
    new_game_table = pa.Table.from_pandas(new_game_data)
    
    pq.write_table(new_game_table, args.output_file)
    print(f"Saved new play-by-play data to {args.output_file}")

    