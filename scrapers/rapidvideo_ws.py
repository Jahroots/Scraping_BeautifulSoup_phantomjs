# coding=utf-8
import time
import re
from urlparse import urlparse
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class RapidvideoWs(SimpleScraperBase):
    BASE_URL = 'http://sexkino.to'
    OTHER_URLS = ['http://xvidstage.com', 'http://rapidvideo.ws', 'http://faststream.ws', 'http://faststream.in']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    SINGLE_RESULTS_PAGE = True

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    TRELLO_ID = 'qa5h7yMK'

    def setup(self):
        super(RapidvideoWs, self).setup()
        self._request_connect_timeout = 300
        self._request_response_timeout = 300

    def _fetch_search_url(self, search_term, media_type):
        return  '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u"Next »")
        if next_button:
            return self.BASE_URL + next_button.href
        return None

    def _parse_search_result_page(self, soup):

        found=0
        for result in soup.select('div.result-item div.title'):
            link = result.select_one('a')
            if link:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
                found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('td#file_title')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        url = soup.select_one('iframe[allowfullscreen]')
        if url:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url['src'],
                link_title=soup.select_one('h2').text,
                series_season=series_season,
                series_episode=series_episode,
            )
