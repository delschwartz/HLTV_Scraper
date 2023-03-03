# Get player stats from X days before the match
def get_player_stats_prior_to_match(match_url, time_delta, sleep_time=0.1):
    """
    Gets individual player stats from the day before to 'time_delta' days before the match.  Returns a nested dict with outer keys (team name, team id), and inner keys (player nick, player id).
    """

    match_html = get_page_html(match_url, sleep_time)

    # Find start and end date for stats to scrape
    match_date_dt = get_match_datetime(match_html)

    start_date_dt = match_date_dt - relativedelta(days = time_delta)
    end_date_dt = match_date_dt - relativedelta(days=1)

    start_date = start_date_dt.strftime("%Y-%m-%d")
    end_date = end_date_dt.strftime("%Y-%m-%d")

    # Get player rosters, clean output, then generate urls
    rosters = get_match_rosters(match_html)

    team1_roster, team2_roster = rosters['team1'], rosters['team2']

    team1_nick_pid = []
    for player in team1_roster:
        nick = player[0]
        pid = player[3]
        team1_nick_pid.append((nick, pid))

    team2_nick_pid = []
    for player in team2_roster:
        nick = player[0]
        pid = player[3]
        team2_nick_pid.append((nick, pid))

    team1_player_stats_urls = []
    for player in team1_nick_pid:
        team1_player_stats_urls.append(get_player_stats_page_url(player[0], player[1], start_date, end_date))

    team2_player_stats_urls = []
    for player in team2_nick_pid:
        team2_player_stats_urls.append(get_player_stats_page_url(player[0], player[1], start_date, end_date))

    team1_player_stats = {}
    for i in range(len(team1_nick_pid)):
        player_stats_html = get_page_html(team1_player_stats_urls[i], sleep_time)
        stats_block = get_player_stats_block(player_stats_html)
        team1_player_stats[team1_nick_pid[i]] = stats_block

    team2_player_stats = {}
    for i in range(len(team2_nick_pid)):
        player_stats_html = get_page_html(team2_player_stats_urls[i], sleep_time)
        stats_block = get_player_stats_block(player_stats_html)
        team2_player_stats[team2_nick_pid[i]] = stats_block

    teams = get_match_teams(match_html)

    player_stats_prior_match = {}
    player_stats_prior_match[teams['team1']] = team1_player_stats
    player_stats_prior_match[teams['team2']] = team2_player_stats

    return player_stats_prior_match
