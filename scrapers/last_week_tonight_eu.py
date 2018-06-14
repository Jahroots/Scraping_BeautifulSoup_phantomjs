# coding=utf-8

from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase

class LastWeekTonightEu(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://last-week-tonight.eu/'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    LONG_SEARCH_RESULT_KEYWORD = 'week'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div.entry-content a'):
            link_text = result.text
            link=None
            if link_text:
                if 'http' in link_text:
                    link = link_text
                elif 'link' in link_text:
                    link = result.href
                if link:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_title=result.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
