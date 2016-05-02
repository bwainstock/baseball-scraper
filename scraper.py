"""
Scrapes baseball player statistics from FanGraphs

"""

import re
import requests
from bs4 import BeautifulSoup



def get_players():
    """
    Downloads list of players on each team and returns a JSON dict of dicts
    """

    #base_url = 'http://www.fangraphs.com'
    base_team_url = 'http://www.fangraphs.com/depthcharts.aspx?position=ALL&teamid={}'
    num_teams = 1
    players_links = {}

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
                if player_name != 'The Others':
                    player_url = player.find('a').attrs['href']
                    player_info = re.search(r"playerid=(\w+)&position=([a-zA-Z0-9_/]+)", player_url)
                    player_id = player_info.group(1)
                    player_position = player_info.group(2)
                else:
                    player_id = 'None'
                    player_position = 'None'
                team_players[player_name] = {'id': player_id, 'position': player_position}
            players_links[team] = team_players

    return players_links

def get_player_stats(player_id, player_position):
    """
    Downloads all stats listed on FanGraphs for player_id at player_position
    """

    base_player_url = \
      'http://www.fangraphs.com/statsd.aspx?playerid={}&position={}&type=&gds=&gde=&season=all'
    url = base_player_url.format(player_id, player_position)

