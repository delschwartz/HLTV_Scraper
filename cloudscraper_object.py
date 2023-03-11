import cloudscraper

cscraper = cloudscraper.create_scraper()

def reset_cloudscraper():
    global cscraper
    cscraper = cloudscraper.create_scraper()
