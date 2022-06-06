import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def nba_players_stats(initial_season, final_season):
    stats_list = []
    for season in range(initial_season, final_season):
        request = request_data_from_season(season)
        soup = parse_request(request)
        table_body = find_table_body(soup)
        players_data = season_total(table_body)
        for player in players_data:
            player_stats = individual_stats(player)
            player_stats.append(season)
            stats_list.append(player_stats)
    table_header = find_table_header(soup)
    columns = generate_df_columns(table_header)
    df = pd.DataFrame(stats_list, columns=columns)
    df = clean_nba_stats_df(df)
    return df


def request_data_from_season(season):
    request = requests.get(f'https://www.basketball-reference.com/leagues/NBA_{season}_per_game.html')
    return request


def parse_request(request):
    soup = BeautifulSoup(request.text, features="html.parser")
    return soup


def find_table_body(soup):
    table = soup.find('table')
    body = table.find('tbody')
    return body


def find_table_header(soup):
    table = soup.find('table')
    header = table.find('thead')
    return header


def generate_df_columns(table_header):
    columns = [i.text for i in table_header.find_all('th')]
    columns = columns[1:]
    columns.append('Season')
    return columns


def season_total(table_body):
    players_data = table_body.find_all('tr', attrs={'class': 'full_table'})
    return players_data


def individual_stats(player):
    player_stats = [x.text for x in player.find_all('td')]
    return player_stats


def clean_nba_stats_df(df):
    df = df.drop('GS', axis=1)  # a lot of missing information on 'GS' column
    df['Player'] = df['Player'].str.strip('*')  # All-Star players had a * in their names
    df.iloc[:, 6:-1] = df.iloc[:, 6:-1].replace('', np.nan).replace(np.nan, 0).astype('float64')  # Game stats to float
    df[['Age', 'G', 'Season']] = df[['Age', 'G', 'Season']].replace('', 0).astype('int64')  # Non-game stats to int
    return df


if __name__ == "__main__":
    stats = nba_players_stats(2017, 2021)
    stats.to_csv('NBA Database.csv', index=False)
    print(stats)
