import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

'''
Scraping data from Basketball Reference
'''
data = []
for i in range(1980, 2022):  # access information for each season
    request = requests.get(f'https://www.basketball-reference.com/leagues/NBA_{i}_per_game.html')
    soup = BeautifulSoup(request.text)
    table = soup.find('table')
    header = table.find('thead')
    body = table.find('tbody')
    players = body.find_all('tr', attrs={'class': 'full_table'})
    for j in players: # get stats for each player in the season
        player_stats = [x.text for x in j.find_all('td')]
        player_stats.append(i)
        data.append(player_stats)


'''
Getting columns name based on last season's link
'''
columns = [i.text for i in header.find_all('th')]
columns = columns[1:]
columns.append('Season')


df = pd.DataFrame(data, columns=columns)


'''
Cleaning data
'''
df = df.drop('GS', axis=1)  # a lot of missing information on 'GS' column
df['Player'] = df['Player'].str.strip('*')  # All-Star players had a * in their names
df.iloc[:, 6:-1] = df.iloc[:, 6:-1].replace('', np.nan).replace(np.nan, 0).astype('float64')  # Game stats to float
df[['Age', 'G', 'Season']] = df[['Age', 'G', 'Season']].replace('', 0).astype('int64')  # Non-game stats to int


'''
Setting only one position per player
'''
position = df.Pos.str.split(pat="-")
position = [i[0] for i in pd.DataFrame(position)['Pos']]
df['Pos'] = position


df.to_csv('Basketball Reference 1980-2021 DB.csv', index=False)
