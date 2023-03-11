# HLTV_Scraper
Unofficial scraper for collecting details &amp; stats from HLTV.org

Work in progress.  This is designed with a specific use in mind but most elements should be useful outside that context.

Current list of functions per file.

### match_parser.py
* get_page_html()
* get_match_datetime()
* get_match_type()
* get_match_teams()
* get_match_score()
* get_match_map_names()
* get_match_map_winners()
* get_match_winner()
* get_match_map_scores()
* get_match_rosters()

### player_stats.py
* get_player_stats_page_url()
* get_player_stats_block()
* get_player_stats_prior_to_match()

### match_stats.py
* nothing yet

### scraper.py
* scrape_match_list()
* scrape_stat_range()

### utilities.py
* update_csv_file()
* check_id_in_csv()
