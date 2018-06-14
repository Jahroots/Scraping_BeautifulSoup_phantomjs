# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import time
import json
import re
class VodlockerPro(SimpleScraperBase):
    BASE_URL = 'https://123movies4u.org'
    OTHER_URLS = ['https://123movies4u.co', 'https://vodlockerb.net', 'https://vodlocker.rocks', 'https://vodlockerfree.com', 'https://vodlocker.cx', 'https://www.vodlocker9.com', 'http://www.vodlockers.pro', 'http://www.vodlocker.pro']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]
    TRELLO_ID = 'B14fegAK'

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USER_NAME = 'Clithapping'
    PASSWORD = 'ofee5Itee'
    EMAIL = 'patriciagcasey@rhyta.com'
    LOGIN_URL = BASE_URL + '/login'
    SINGLE_RESULTS_PAGE = True
    REQUIRES_WEBDRIVER = ('parse',)

    def setup(self):
        super(VodlockerPro, self).setup()
        self._request_response_timeout = 600
        self._request_connect_timeout = 600

    def _fetch_search_url(self, search_term, media_type):
        return '{}/ajax/search.php'.format(self.BASE_URL)

    def _fetch_no_results_text(self):
        return u"Unfortunately we couldn't find"

    def _fetch_next_button(self, soup):
        return None

    def login(self):
        return self.post_soup(self.LOGIN_URL, data = {'returnpath' : '/', 'username' : self.USER_NAME, 'password' : self.PASSWORD})

    def search(self, search_term, media_type, **extra):
        soup = self.login()
        soup = self.post(self._fetch_search_url(search_term, media_type), data = {'q': search_term, 'limit' :  100, 'timestamp': time.time()}).text
        items = json.loads(soup)
        self._parse_search_result_page(items)

    def _parse_search_result_page(self, items):
        if not items and len(items) == 0:
            return self.submit_search_no_results()

        for item in items:
            link = item['permalink']
            title = item['title']
            soup = self.get_soup(link)
            link = soup.select_one('#mv-info a')
            if 'javascript' not in link.href:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=title,
                )

    def parse(self, parse_url, **extra):
        soup = self.login()
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        link = soup.select_one('div iframe')
        if link:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=title.text,
                series_season=series_season,
                series_episode=series_episode,
            )

        for url in self.util.find_urls_in_text(soup.find('script', text=re.compile('embeds')).text):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=title.text,
                series_season=series_season,
                series_episode=series_episode,
            )
