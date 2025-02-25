def player_per100poss(season):
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
        url = f"https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=&PaceAdjust=N&PerMode=Per100Possessions&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=&TwoWay=&VsConference=&VsDivision=&Weight="
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
            
            player_data = await fetch_play_by_play(session, season)
            
            # Concatenate all play-by-play data into a single DataFrame
            return player_data
            
            
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
    season = "2024-25"
    player_data = player_per100poss(season)
    player_data['SEASON'] = season
    print(player_data.head(10))
    pq.write_table(pa.Table.from_pandas(player_data), f'{season}player_per100poss.parquet')
    
    
    