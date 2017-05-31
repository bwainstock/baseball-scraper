# pylint: disable=C0103,R0914
# disables invalid names (C0103) and too many local variables (R0914)
"""
Scrapes baseball player statistics from FanGraphs

"""

import re
import sqlite3
from bs4 import BeautifulSoup
import requests


conn = sqlite3.connect('fangraphs.db')
conn.row_factory = sqlite3.Row

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
                    if player_position != 'P':
                        try:
                            with conn:
                                conn.execute("""INSERT INTO players VALUES
                                            (?,?, ?)""", (player_id, player_name, player_position))
                                print('{} inserted'.format(player_name))
                                conn.commit()
                        except sqlite3.IntegrityError:
                            print("Can't insert {}".format(player_name))
                    else:
                        try:
                            with conn:
                                conn.execute("""INSERT INTO pitchers VALUES
                                            (?,?, ?)""", (player_id, player_name, player_position))
                                print('{} inserted'.format(player_name))
                                conn.commit()
                        except sqlite3.IntegrityError:
                            print("Can't insert {}".format(player_name))
                else:
                    player_id = 'None'
                    player_position = 'None'
                team_players[player_name] = {'id': player_id, 'position': player_position}
            players_links[team] = team_players

    return players_links


def parse_pitcher_stats(date_info, player_id, player_position):
    """
    Downloads stats for pitchers
    """
    date_stats = date_info.findAll('td')

    date = date_stats[0].text.strip()
    print(date)
    team = date_stats[1].text.strip()
    opp = date_stats[2].text.strip()
    gs = date_stats[3].text.strip()
    w = date_stats[4].text.strip()
    l = date_stats[5].text.strip()
    era = date_stats[6].text.strip()
    g = date_stats[7].text.strip()
    cg = date_stats[9].text.strip()
    sho = date_stats[10].text.strip()
    sv = date_stats[11].text.strip()
    hld = date_stats[12].text.strip()
    bs = date_stats[13].text.strip()
    ip = date_stats[14].text.strip()
    tbf = date_stats[15].text.strip()
    h = date_stats[16].text.strip()
    r = date_stats[17].text.strip()
    er = date_stats[18].text.strip()
    hr = date_stats[19].text.strip()
    bb = date_stats[20].text.strip()
    ibb = date_stats[21].text.strip()
    hbp = date_stats[22].text.strip()
    wp = date_stats[23].text.strip()
    bk = date_stats[24].text.strip()
    so = date_stats[25].text.strip()
    gsv2 = date_stats[26].text.strip()

    stats = (player_id, player_position, date, team, opp, gs, w, l, era,
             g, cg, sho, sv, hld, bs, ip, tbf, h, r, er, hr, bb, ibb,
             hbp, wp, bk, so, gsv2)

    return stats


def parse_player_stats(date_info, player_id, player_position):
    """
    Downloads stats for players
    """
    date_stats = date_info.findAll('td')

    date = date_stats[0].text.strip()
    print(date)
    team = date_stats[1].text.strip()
    opp = date_stats[2].text.strip()
    bo = date_stats[3].text.strip()
    g = date_stats[5].text.strip()
    ab = date_stats[6].text.strip()
    pa = date_stats[7].text.strip()
    h = date_stats[8].text.strip()
    b1 = date_stats[9].text.strip()
    b2 = date_stats[10].text.strip()
    b3 = date_stats[11].text.strip()
    hr = date_stats[12].text.strip()
    r = date_stats[13].text.strip()
    rbi = date_stats[14].text.strip()
    bb = date_stats[15].text.strip()
    ibb = date_stats[16].text.strip()
    so = date_stats[17].text.strip()
    hbp = date_stats[18].text.strip()
    sf = date_stats[19].text.strip()
    sh = date_stats[20].text.strip()
    gdp = date_stats[21].text.strip()
    sb = date_stats[22].text.strip()
    cs = date_stats[23].text.strip()
    avg = date_stats[24].text.strip()

    stats = (player_id, player_position, date, team,
             opp, bo, g, ab, pa, h, b1, b2, b3,
             hr, r, rbi, bb, ibb, so, hbp, sf, sh, gdp, sb, cs, avg)
    return stats


def insert_stats(stats, player_category):
    """
    Inserts stats into db_name and returns 1 if true
    """
    if player_category == 'player':
        conn.execute("""INSERT INTO player_stats VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", stats)
        conn.commit()
        db_name = 'player_stats'
        print('inserted player')
    if player_category == 'pitcher':
        db_name = 'pitcher_stats'
        conn.execute("""INSERT INTO pitcher_stats VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", stats)
        conn.commit()
        print('inserted pitcher')

def get_stats(player_id, player_position):
    """
    Downloads all stats listed on FanGraphs for player_id at player_position
    """

    base_player_url = \
      'http://www.fangraphs.com/statsd.aspx?playerid={}&position={}&type=1&gds=&gde=&season=all'
    url = base_player_url.format(player_id, player_position)
    regex_row = r"rg(Alt)?Row"
    all_stats = []

    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    dates = soup.findAll('tr', class_=re.compile(regex_row))
    for date_info in dates:
        if 'Total' not in date_info.find('td').text:
            if player_position == 'P':
                print(url)
                stats = parse_pitcher_stats(date_info, player_id, player_position)
                insert_stats(stats, 'pitcher')
            else:
                print(url)
                stats = parse_player_stats(date_info, player_id, player_position)
                insert_stats(stats, 'player')
    return all_stats


def create_tables():
    """
    Creates Pitchers and Players tables if they don't exist in the db
    """

    conn.execute('''CREATE TABLE IF NOT EXISTS pitchers (
                id text primary key,
                name text,
                position text)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS players (
                id text primary key,
                name text,
                position text)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS pitcher_stats (
                id text,
                position text,
                date text,
                team text,
                opp text,
                gs real,
                w real,
                l real,
                era real,
                g real,
                cg real,
                sho real,
                sv real,
                hld real,
                bs real,
                ip real,
                tbf real,
                h real,
                r real,
                er real,
                hr real,
                bb real,
                ibb real,
                hbp real,
                wp real,
                bk real,
                so real,
                gsv2 real)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS player_stats (
                id text,
                position text,
                date text,
                team text,
                opp text,
                bo real,
                g real,
                ab real,
                pa real,
                h real,
                b1 real,
                b2 real,
                b3 real,
                hr real,
                r real,
                rbi real,
                bb real,
                ibb real,
                so real,
                hbp real,
                sf real,
                sh real,
                gdp real,
                sb real,
                cs real,
                avg real)''')

def dbconn():
    """
    Sets up DB connection are returns cursor
    """
    return conn


def main():
    """Main function"""
    create_tables()
    players = get_players()
    for team in players:
        for player in players[team]:
            player_id = players[team][player]['id']
            position = players[team][player]['position']
            get_stats(player_id, position)
    conn.close()

if __name__ == '__main__':
    main()
