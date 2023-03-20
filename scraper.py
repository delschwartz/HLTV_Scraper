import datetime as dt

from utilities import *
from match_parser import *
from player_stats import *
# from match_stats import *

def scrape_match_list(start_date, end_date, sleep_time = 0.05, update_csv=True):
    """
    Gets list of all matches in date range.  List format: ['ID', 'DATE', 'TITLE', 'URL', 'TEAMS', 'WINNER', 'SCORE']
    Saves to csv by default.
    Does not check if matches within date range are already saved.
    """

    check_date_range(start_date, end_date)

    start_date_dt = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = dt.datetime.strptime(end_date, '%Y-%m-%d')
    feb_2016_dt = dt.datetime.strptime("2016-02-01", '%Y-%m-%d')

    if start_date_dt <= feb_2016_dt <= end_date_dt:
        print("Warning: 2016-02-01 is between the start and end dates. HLTV changed player rating systems on 2016-02-01, some player stats may not be consistently measured over this date range.")

    results_url = f"https://www.hltv.org/results?startDate={start_date}&endDate={end_date}"

    match_list = []

    next_page_exists = True
    while next_page_exists:

        results_page_html = get_page_html(results_url, sleep_time = sleep_time)
        results_holder = results_page_html.find('div', {'class':'results-holder allres'})
        match_list_htmls = results_holder.find_all('div', {'class':'result-con'})

        for match in match_list_htmls:
            match_url = "https://www.hltv.org" + match.find('a', {'class':'a-reset'})['href']
            match_id, match_title = get_match_id_title(match_url)
            match_date_unix = match['data-zonedgrouping-entry-unix']
            match_date = dt.datetime.fromtimestamp(int(match_date_unix)/1000).strftime('%Y-%m-%d')

            # Extract the scores from the HTML code
            scores = match.find_all('span', {'class': ['score-lost', 'score-won', 'score-tie']})
            try:
                team1_score = int(scores[0].text)
                team2_score = int(scores[1].text)
            except:
                team1_score, team2_score = None, None
                print("Error at: ", match_url, ",  ", results_url)
            score = (team1_score, team2_score)

            # Determine the winner of the match
            teams_html = match.find_all('div', {'class': 'team'})
            team1_name = teams_html[0].text.strip()
            team2_name = teams_html[1].text.strip()
            teams = (team1_name, team2_name)

            if team1_score > team2_score:
                winner = 'team1'
            elif team2_score > team1_score:
                winner = 'team2'
            else:
                winner = 'tie'

            match_list.append([match_id, match_date, match_title, match_url, teams, winner, score])

        try:
            next_page_url = "https://www.hltv.org" + results_page_html.find('a', {'class':'pagination-next'})['href']
            results_url = next_page_url
        except:
            next_page_exists = False

    if update_csv:
        update_csv_file('data\match_list.csv', match_list, ['id', 'date', 'title', 'url', 'teams', 'winner', 'score'])

    return match_list


def scrape_stat_range(match_list, player_stat_range, return_output=False, sleep_time = 0.05, update_stats_csv = True, update_players_csv = True, update_teams_csv = True):
    """
    Scrapes player stats player_stat_range days prior to each match in match_list.
    Saves to csv by default.
    Stats must be retrieved as ordered dict to keep team1/team2 consistent.
    """

    start_timer()
    print(f"Getting player stats for {player_stat_range} days prior to each match.")
    print()

    stats_csv = f"data\match_player_stats_prev_{player_stat_range}.csv"


    # Pull list of match IDs from csv
    matches_ids_from_file = []
    if os.path.exists(stats_csv):
        with open(stats_csv, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for row in csvreader:
                matches_ids_from_file.append(row[0])

    # Pull list of player IDs from csv
    if update_players_csv:
        players_csv = "data\players.csv"
        player_ids_from_file = []
        if os.path.exists(players_csv):
            with open(players_csv, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                next(csvreader)
                for row in csvreader:
                    player_ids_from_file.append(row[0])


    # Pull list of team IDs from csv
    if update_teams_csv:
        teams_csv = "data\teams.csv"
        team_ids_from_file = []
        if os.path.exists(teams_csv):
            with open(teams_csv, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                next(csvreader)
                for row in csvreader:
                    team_ids_from_file.append(row[0])



    new_match_ids = [match[0] for match in match_list if match[0] not in matches_ids_from_file]
    saved_new_match_ids = [match[0] for match in match_list if match[0] in matches_ids_from_file]
    new_matches = [match for match in match_list if match[0] in new_match_ids]

    total_matches = len(match_list)
    total_new = len(new_match_ids)
    total_saved_new_matches = len(saved_new_match_ids)

    print(f"Input match list contains {total_matches} matches.")

    if os.path.exists(stats_csv):
        print(f"{total_saved_new_matches} of match list already saved in {stats_csv}.")

    print(f"Processing {total_new} new matches.")


    match_player_data = []

    for match in new_matches:

        match_url = match[3]
        match_id = get_match_id_title(match_url)[0]


        print("-Processing: " + match_url)
        match_html = get_page_html(match_url)

        player_stats = get_player_stats_prior_to_match(match_html, player_stat_range, sleep_time)
        match_player_data.append([match[0], player_stats])

    if update_stats_csv:
        update_csv_file(stats_csv, match_player_data, ['id', 'stats'])

    print()
    end_timer()

    if return_output:
        return match_player_data
