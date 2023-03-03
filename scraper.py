def get_results_list(start_date, end_date, sleep_time = 0.1):
    """
    Gets list of all matches in date range.  List format: [id, title, url]
    """

    results_url = f"https://www.hltv.org/results?startDate={start_date}&endDate={end_date}"

    match_list = []

    next_page_exists = True
    while next_page_exists:

        results_page_html = get_page_html(results_url, sleep_time = sleep_time)

        results_holder = results_page_html.find('div', {'class':'results-holder allres'})

        match_list_htmls = results_holder.find_all('a', {'class':'a-reset'})

        for match in match_list_htmls:
            match_url = "https://www.hltv.org" + match['href']
            match_id, match_title = get_match_id_title(match_url)
            match_list.append([match_id, match_title, match_url])

        try:
            next_page_url = "https://www.hltv.org" + results_page_html.find('a', {'class':'pagination-next'})['href']
            results_url = next_page_url
        except:
            next_page_exists = False

    return match_list
