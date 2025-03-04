def player_heights(players):
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


    async def fetch_heights(session, player):
        url = f"https://stats.nba.com/stats/commonplayerinfo?LeagueID=&PlayerID={player}"
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                row =  pd.DataFrame(data['resultSets'][0]['rowSet'], columns=data['resultSets'][0]['headers'])
                height = row['HEIGHT'].values[0]
                value = {'PLAYER_ID': player, 'HEIGHT': height}
                df = pd.DataFrame([value])
                return df
            else:
                return pd.DataFrame()

    async def main():
        async with aiohttp.ClientSession() as session:
            total_player_data = pd.DataFrame()
            for player in players:
                player_data = await fetch_heights(session, player)
                total_player_data = pd.concat([total_player_data, player_data], ignore_index=True)
            # Concatenate all play-by-play data into a single DataFrame
            return total_player_data
            
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

    file_path = 'data/00_24_anthro.parquet'
    existing_data = pd.read_parquet(file_path)
    missing_height_player_ids = existing_data[existing_data['HEIGHT_WO_SHOES'].isna()]['PLAYER_ID'].tolist()
    print(f"Missing {len(missing_height_player_ids)} player heights")
    heights = player_heights(missing_height_player_ids)
    print(len(heights))
    heights['HEIGHT_WO_SHOES'] = heights['HEIGHT'].apply(lambda x: (int(x.split('-')[0])*12 + int(x.split('-')[1]))-1.5 if x else None)
    heights['WINGSPAN'] = heights['HEIGHT_WO_SHOES']*1.06
    merged_data = existing_data.merge(heights, on='PLAYER_ID', how='left', suffixes=('','_temp'))
    merged_data['HEIGHT_WO_SHOES'] = merged_data['HEIGHT_WO_SHOES'].fillna(merged_data['HEIGHT_WO_SHOES_temp'])
    merged_data['WINGSPAN'] = merged_data['WINGSPAN'].fillna(merged_data['WINGSPAN_temp'])
    merged_data = merged_data.drop(columns=['HEIGHT_WO_SHOES_temp', 'WINGSPAN_temp'])
    print(len(merged_data['HEIGHT_WO_SHOES'].isna()))   
    merged_data.to_parquet(file_path, index=False)
    
    