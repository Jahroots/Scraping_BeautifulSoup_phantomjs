# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CacheableParseResultsMixin, SimpleGoogleScraperBase

class SeventeenWtvCom(CacheableParseResultsMixin, SimpleGoogleScraperBase, SimpleScraperBase):
    BASE_URL = 'https://www.17wtv.com'
    OTHER_URLS = ['http://www.17wtv.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'chi'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    LONG_SEARCH_RESULT_KEYWORD = 'the'
    SINGLE_RESULTS_PAGE = True

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.next')
        if next_button:
            return next_button.href
        return None

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('iframe[allowfullscreen]') + soup.select('p iframe'):
            source_link = result['src']
            if 'http' not in source_link:
                source_link='http:'+source_link
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=source_link,
                link_title=result.text,
                series_season=series_season,
                series_episode=series_episode,
            )
