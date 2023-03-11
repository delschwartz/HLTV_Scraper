import re
import datetime as dt
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from match_parser import *

# Get player stats page url
def get_player_stats_page_url(player_nick, player_id, start_date = None, end_date = None, on_maps = None):

    """
    Gets player stats page URL.  Date range and map are optional.  If not specified will return URL for all time stats on all maps.
    IMPORTANT:  Only use start dates from February 2016 onwards.  Stats pages containing data older than February 2016, as well as players' career stats, use a different rating system.
    """

    # Check dates are in correct format
    for date in [start_date, end_date]:
        if date != None:
            try:
                dt.datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Dates must be None or a string in the format 'yyyy-mm-dd'")

    # Check that start_date is before end_date
    if (start_date != None and end_date != None):
        start_date_dt = dt.datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = dt.datetime.strptime(end_date, "%Y-%m-%d")
        if start_date >= end_date:
            raise ValueError("start_date must be before end_date")

    player_id = str(player_id)

    link_prefix = f"https://www.hltv.org/stats/players/{player_id}/{player_nick}/?"

    start_date_url, end_date_url, map_url = "", "", ""

    if start_date != None:
        start_date_url = "startDate=" + start_date

    if end_date != None:
        end_date_url = "endDate=" + end_date

    if on_maps != None:
        if type(on_maps) == str:
            map_url = "maps=" + on_maps
        if type(on_maps) == list:
            map_url = "maps=" + '&maps='.join(on_maps)

    template_url_parts = [start_date_url, end_date_url, map_url]
    url_parts = [part for part in template_url_parts if part != ""]

    stats_url = link_prefix + '&'.join(url_parts)
    return stats_url


# This is messy, could be cleaned up but it works fine as is.
def get_player_stats_block(player_stats_html):
    """
    Gets both basic stats blocks on player stats page.
    IMPORTANT: This function does not know dates or maps.  Those must be tracked separate from this function.
    """
    stat_types_1 = []
    modified_list = []
    stat_values_str = []
    stat_values = []

    # First summary stat block
    summaryBreakdownContainer = player_stats_html.find('div', {'class': 'summaryBreakdownContainer'})
    summaryStatBreakdownRow = summaryBreakdownContainer.find_all('div', {'class':'summaryStatBreakdownRow'})
    summaryStatBreakdown = summaryBreakdownContainer.find_all('div', {'class': re.compile(r"summaryStatBreakdown (.*)")})

    for stat_html in summaryStatBreakdown:
        stat_types_1.append(stat_html.find('div', {'class':'summaryStatBreakdownSubHeader'}).find('b').text)
        stat_values_str.append(stat_html.find('div', {'class':'summaryStatBreakdownDataValue'}).text)

    # Second stat block
    stat_block_html = player_stats_html.find('div', {'class': 'statistics'})
    stats_rows = stat_block_html.find_all('div', {'class':'stats-row'})

    stat_types_2 = []
    for row in stats_rows:
        stat_types_2.append(row.find('span').text)

    for stat_type in stat_types_2:
        stat_values_str.append(stat_block_html.find('span', text=stat_type).find_next_sibling('span').text)

    stat_types = stat_types_1 + stat_types_2

    for item in stat_types:
        modified_item = item.lower().replace(' / ', '_per_').replace('/','').replace(' ', '_').replace('%', 'percent').replace('.0','')
        modified_list.append(modified_item)

    for item in stat_values_str:
        if item[-1] == '%':
            stat_values.append(float(item[:-1])/100)
        else:
            stat_values.append(float(item))

    stats_dict = dict(zip(modified_list, stat_values))
    return stats_dict


# Get player stats from X days before the match
def get_player_stats_prior_to_match(match_html, player_stat_range, sleep_time=0.1):
    """
    Gets player stats from the day before to 'player_stat_range' days before the match.  Returns a nested dict with outer keys (team name, team id), and inner keys (player nick, player id).
    """

    # Find start and end date for stats to scrape
    match_date_dt = get_match_datetime(match_html)

    start_date_dt = match_date_dt - relativedelta(days = player_stat_range)
    end_date_dt = match_date_dt - relativedelta(days=1)

    start_date = start_date_dt.strftime("%Y-%m-%d")
    end_date = end_date_dt.strftime("%Y-%m-%d")

    # Get player rosters, clean output, then generate urls
    rosters = get_match_rosters(match_html)

    team1_roster, team2_roster = rosters['team1'], rosters['team2']

    team1_player_stats_urls = []
    for pid, nick in team1_roster:
        team1_player_stats_urls.append(get_player_stats_page_url(nick, pid, start_date, end_date))

    team2_player_stats_urls = []
    for pid, nick in team2_roster:
        team2_player_stats_urls.append(get_player_stats_page_url(nick, pid, start_date, end_date))

    team1_player_stats = {}
    for i in range(len(team1_roster)):
        player_stats_html = get_page_html(team1_player_stats_urls[i], sleep_time)
        stats_block = get_player_stats_block(player_stats_html)
        team1_player_stats[team1_roster[i]] = stats_block

    team2_player_stats = {}
    for i in range(len(team2_roster)):
        player_stats_html = get_page_html(team2_player_stats_urls[i], sleep_time)
        stats_block = get_player_stats_block(player_stats_html)
        team2_player_stats[team2_roster[i]] = stats_block

    teams = get_match_teams(match_html)

    player_stats_prior_match = {}
    player_stats_prior_match[teams['team1']] = team1_player_stats
    player_stats_prior_match[teams['team2']] = team2_player_stats

    return player_stats_prior_match
