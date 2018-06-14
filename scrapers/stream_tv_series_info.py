# coding=utf-8
import time
from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase

class StreamTvSeriesInfo(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://mystream-tv.one'
    OTHER_URLS = [
        'http://stream-tv9.com',
        'http://stream-tv8.me',
        'http://stream-tv7.co',
        'http://stream-tv6.me',
        'http://stream-tv4.me',
        'http://stream-tv-series.info',
        'http://stream-tv3.co',
        'http://stream-tv3.me',
        'http://stream-tv2.ag',
        'http://streamtvlinks.me',
        'http://stream-tv-series.net',
        'http://stream-tv2.to']

    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    TRELLO_ID = 'O4QSIF1l'

    def setup(self):
        super(StreamTvSeriesInfo, self).setup()
        self._request_connect_timeout = 600
        self._request_response_timeout = 600

    def _parse_parse_page(self, soup):

        if soup.find('strong', text ='Episode List'):
            links = soup.select('ul li a')
            for link in links:
                soup = self.get_soup(link.href)

                index_page_title = self.util.get_page_title(soup)
                series_season = series_episode = None
                title = soup.select_one('h1')
                if title and title.text:
                    series_season, series_episode = self.util.extract_season_episode(title.text)
                for link in soup.select('div.postTabs_divs iframe'):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link['src'],
                        link_title=link.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )