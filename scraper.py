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
      'http://www.fangraphs.com/statsd.aspx?playerid={}&position={}&type=1&gds=&gde=&season=all'
    url = base_player_url.format(player_id, player_position)
    print(url)
    regex_row = r"rg(Alt)?Row"
    all_stats = []

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    dates = soup.findAll('tr', class_=re.compile(regex_row))
    for date_info in dates:
        if 'Total' not in date_info.find('td').text:
            date_stats = date_info.findAll('td')

            DATE = date_stats[0].text
            print(DATE)
            TEAM = date_stats[1].text
            OPP = date_stats[2].text
            GS = date_stats[3].text
            W = date_stats[4].text
            L = date_stats[5].text
            ERA = date_stats[6].text
            G = date_stats[7].text
            GS = date_stats[8].text
            CG = date_stats[9].text
            ShO = date_stats[10].text
            SV = date_stats[11].text
            HLD = date_stats[12].text
            BS = date_stats[13].text
            IP = date_stats[14].text
            TBF = date_stats[15].text
            H = date_stats[16].text
            R = date_stats[17].text
            ER = date_stats[18].text
            HR = date_stats[19].text
            BB = date_stats[20].text
            IBB = date_stats[21].text
            HBP = date_stats[22].text
            WP = date_stats[23].text
            BK = date_stats[24].text
            SO = date_stats[25].text
            GSv2 = date_stats[26].text

            all_stats.append((player_id, player_position, DATE, TEAM, OPP, GS, W, L, ERA,
                              G, GS, CG, ShO, SV, HLD, BS, IP, TBF, H, R, ER, HR, BB, IBB,
                              HBP, WP, BK, SO, GSv2))
    return all_stats
