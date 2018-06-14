# coding=utf-8
import time
from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase

class Filme3dNet(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://filme3d.net'
    OTHER_URLS = ['http://www.filme3d.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    # search does not work on the website.

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div.repro_layer iframe'):
            link = result['src']
            if link.startswith('//'):
                link = 'http:'+link
            if 'youtube' in link:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_title=result.text,
                series_season=series_season,
                series_episode=series_episode,
            )
