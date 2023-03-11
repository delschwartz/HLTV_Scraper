import re
from datetime import datetime
from bs4 import BeautifulSoup
from time import sleep
import requests
import pytz

# from cloudscraper_object import cscraper, reset_cloudscraper
import cloudscraper

# Must run get_match_html before any other get functions.  All other functions require match page html as input.
# This is to help avoid rate limiting from hltv.org (and to optimize perforamce)

def get_page_html(url, sleep_time=0):
    """
    Gets full html for match page. Optional sleep timer for rate limiting.
    """
    sleep(sleep_time)
    cscraper = cloudscraper.create_scraper()
    response = cscraper.get(url)
    html = response.text
    match_html = BeautifulSoup(html, 'html.parser')
    return match_html

# Get match id and title
def get_match_id_title(match_url, from_html=False):

    # if statement adds ability to pull id & title from the page html
    if from_html:
        match_html = match_url
        match_url = match_html.find('head').find('link', {'rel':'canonical'})['href']

    match = re.search(r"/matches/(\d+)/(.+)$", match_url)

    if match:
        match_id = match.group(1)
        match_title = match.group(2).replace('-', '_')

    return match_id, match_title


# Get match date & time in unix format
def get_match_datetime(match_html):
    """
    Get match date & time in unix format. Takes full match page html as argument.
    """

    date = match_html.find('div', {'class': 'timeAndEvent'}).find('div', {'class': 'date'})
    unix_time = date['data-unix']
    ts = int(unix_time)
    match_date_time = datetime.fromtimestamp(ts/1000)
    return match_date_time

# Get match type
def get_match_type(match_html):
    """
    Get match type.
    Returns: (best_of, event_type)
    """
    type_html = match_html.find('div', {'class': 'standard-box veto-box'}).find('div', {'class': "padding preformatted-text"})
    type_text = type_html.text

    best_of = re.findall(r"Best of (\d+)" ,type_text)[0]

    event_type = re.search(r"\((.*?)\)", type_text)[0].strip("()")

    return int(best_of), event_type


# Get teams
def get_match_teams(match_html):
    """
    Get teams and team ids from full match page html.  Returns dictioary. Keys: team1, team2.  Values: tuples (team_name, team_id).
    """
    teams = {}

    html1_text = match_html.find('div', {'class': 'team1-gradient'})
    id_text = html1_text.find('a')
    lst = id_text['href'].split('/')
    team1_id = lst[2]

    name_text = html1_text.find('div', {'class': 'teamName'})
    team1_name = name_text.text

    teams['team1'] = (team1_name, team1_id)


    html2_text = match_html.find('div', {'class': 'team2-gradient'})
    id_text = html2_text.find('a')
    lst = id_text['href'].split('/')
    team2_id = lst[2]

    name_text = html2_text.find('div', {'class': 'teamName'})
    team2_name = name_text.text

    teams['team2'] = (team2_name, team2_id)

    return teams

# Get match score
def get_match_score(match_html, team1 = 'team1', team2 = 'team2'):
    """
    Gets match score and winner.  Returns dict {'team1 score': score, 'team2 score': score, winner: team1 or team2}
    """
    score = {}

    score1_html = match_html.find('div', {'class': 'standard-box teamsBox'}).find('div', {'class': "team1-gradient"})
    score1_text_html = score1_html.find('div', {'class': re.compile("won|lost")})
    team1_score = score1_text_html.text

    score2_html = match_html.find('div', {'class': 'standard-box teamsBox'}).find('div', {'class': "team2-gradient"})
    score2_text_html = score2_html.find('div', {'class': re.compile("won|lost")})
    team2_score = score2_text_html.text

    score[team1] = team1_score
    score[team2] = team2_score

    team1_winner = score1_text_html['class'][0] == 'won'
    if team1_winner: winner = team1

    team2_winner = score2_text_html['class'][0] == 'won'
    if team2_winner: winner = team2

    score['winner'] = winner

    return score

# Get match_maps
def get_match_map_names(match_html, exclude_not_played = True):
    """
    Returns list of maps played in play order.  Optionally can include list of maps not played as second list.
    """

    maps_picked_html = match_html.find('div', {'class': 'flexbox-column'}).find_all('div', {'class':'mapholder'})

    # Includes map html snippet only if it has class="played"
    maps_played_html = [map_picked for map_picked in maps_picked_html if len(map_picked.find_all('div', {'class': 'played'})) != 0]
    maps_played = [map_played.find('div', {'class': 'mapname'}).text for map_played in maps_played_html]

    if exclude_not_played: return maps_played


    # Same except class must be "optional"
    maps_not_played_html = [map_picked for map_picked in maps_picked_html if len(map_picked.find_all('div', {'class': 'optional'})) != 0]
    maps_not_played = [map_played.find('div', {'class': 'mapname'}).text for map_played in maps_not_played_html]
    if len(maps_not_played) == 0:
        maps_not_played = None

    return maps_played, maps_not_played

# Get map winner
def get_match_map_winners(match_html, team1 = 'team1', team2 = 'team2'):
    """
    Returns ordered list of which team won each map.
    """
    results_played_html = match_html.find_all('div', {'class':'results played'})

    # Check left results only

    map_winners = []

    for i in range(len(results_played_html)):
        left_winner = results_played_html[i].find_all('div', {'class':re.compile('results-left won.*')})
        if left_winner:
            map_winners.append(team1)
        else:
            map_winners.append(team2)

    return map_winners



# Get match winner
def get_match_winner(match_html, team1 = 'team1', team2 = 'team2'):
    """
    Only returns the match winner.
    """
    result = match_html.find('div', {'class':'team1-gradient'}).find('div', {'class':'won'})

    if result != None:
        return team1
    else:
        return team2

# Get map scores

def get_match_map_scores(match_html, team1 = 'team1', team2 = 'team2', map_names = None):

    result_left_list = match_html.find_all('div', {'class':'results-left'})
    result_right_list = match_html.find_all('span', {'class':'results-right'})

    scores = []
    for i in range(len(result_left_list)):
        team1_score = result_left_list[i].find('div', {'class': 'results-team-score'}).text
        team2_score = result_right_list[i].find('div', {'class': 'results-team-score'}).text
        try:
            team1_score = int(team1_score)
            team2_score = int(team2_score)
            scores.append([team1_score, team2_score])
        except:
            next

    return scores

# Get match rosters - Uses lineups instead of stats table since stats table is sometimes missing
def get_match_rosters(match_html):
    """
    Returns dictionary with 4 keys.  team1_name, team2_name, team1_roster, team2_roster.
    Each roster is a list of tuples.  (id, nickname)
    """

    lineups_html = match_html.find_all('div', {'class':'lineup standard-box'})

    team1_name = lineups_html[0].find('a', {'class': 'text-ellipsis'}).text
    team2_name = lineups_html[1].find('a', {'class': 'text-ellipsis'}).text

    team1_players_html = lineups_html[0].select('td.player:not(.player-image)')
    team2_players_html = lineups_html[1].select('td.player:not(.player-image)')

    team1_roster =[]

    for player in team1_players_html:
        player_div = player.find('div', class_='text-ellipsis')
        player_nickname = player_div.text
        player_id = player_div.parent['data-player-id']
        team1_roster.append((player_id, player_nickname))


    team2_roster =[]

    for player in team2_players_html:
        player_div = player.find('div', class_='text-ellipsis')
        player_nickname = player_div.text
        player_id = player_div.parent['data-player-id']
        team2_roster.append((player_id, player_nickname))

    rosters = {}

    rosters['team1_name'] = team1_name
    rosters['team1'] = team1_roster
    rosters['team2_name'] = team2_name
    rosters['team2'] = team2_roster

    return rosters
