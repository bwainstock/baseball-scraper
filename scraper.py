"""
Scrapes baseball player statistics from FanGraphs

"""

from bs4 import BeautifulSoup
import requests


players_links = {}

def get_players():
    """
    Downloads list of players on each team and returns a JSON dict of dicts
    """

    base_url = 'http://www.fangraphs.com'
    base_team_url = 'http://www.fangraphs.com/depthcharts.aspx?position=ALL&teamid={}'
    num_teams = 30

    for team_id in range(1, num_teams+1):
        url = base_team_url.format(team_id)
        resp = requests.get(url)
        if 'errorpath' not in resp.url:
            soup = BeautifulSoup(resp.text, 'html.parser')
            team = soup.find('table', attrs={'class': 'depth_chart'}).findPrevious('span')
            team = team.text.strip()
            print(team)
            players = soup.findAll('tr', attrs={'class': 'depth_reg'})
            players = [player.find('td') for player in players]
            team_players = {}
            for player in players:
                player_name = player.text.strip()
                print(player_name)
                if player_name != 'The Others':
                    player_url = '/'.join([base_url, player.find('a').attrs['href']])
                else:
                    player_url = 'None'
                team_players[player_name] = player_url
            players_links[team] = team_players

    return players_links
