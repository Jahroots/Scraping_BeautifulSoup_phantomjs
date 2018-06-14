# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin
import base64
import re
class YaskeTo(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://peliculas.yaske.ro'
    OTHER_URLS = ['http://series.yaske.ro','http://www.yaske.ro', 'http://yaske.ro', 'http://www.yaske.cc', 'http://kids.yaske.ro']

    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ]
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    SEARCH_TERM = ''
    PAGE = 2

    def _fetch_no_results_text(self):
        return None#'Lo sentimos no encontramos lo que estas buscando'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?query=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.select_one('a[href*="/search/movie/?query={}&page={}"]'.format(self.SEARCH_TERM, str(self.PAGE)))
        if link:
            self.PAGE += 1
            return self.BASE_URL + link['href']
        return None

    def make_soup(self, content, url=None, from_encoding=None):
        content = unicode(content, errors='ignore')
        return super(YaskeTo, self).make_soup(content, url=url, from_encoding=from_encoding)

    def get(self, url, **kwargs):
        return super(YaskeTo, self).get(url, **kwargs)

    def search(self, search_term, media_type, **extra):
        self.SEARCH_TERM = search_term
        self.PAGE = 2
        super(YaskeTo, self).search(search_term, media_type, **extra)

    def _parse_search_result_page(self, soup):

        results = soup.select('a[class="post-item-image btn-play-item"]')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                    link_url= result['href'],
                    link_title=result.text.strip(),
                )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)

    def _video_player_classes(self):
        return ()

    def _video_player_ids(self):
        return ('BoxPlayerTabs2', 'BoxPlayerTabs' )

    def _packet_matches_playlist(self, packet):
        return False

    def parse(self, parse_url, **extra):
        self.webdriver().get(parse_url)
        link = self.webdriver().find_element_by_css_selector('iframe').get_property('src')
        soup = self.get_soup(link)
        links = soup.select('a')

        for link in links:
            soup = self.get_soup('http://widget.olimpo.link' + link.href)
            iframe = soup.select_one('iframe')
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=iframe['src']
            )