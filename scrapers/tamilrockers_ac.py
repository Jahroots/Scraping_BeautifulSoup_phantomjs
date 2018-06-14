# coding=utf-8

from sandcrawler.scraper import ScraperBase, CachedCookieSessionsMixin, DuckDuckGo, CloudFlareDDOSProtectionMixin
from sandcrawler.scraper.caching import cacheable
import re

class TamilrockersAc(CloudFlareDDOSProtectionMixin, DuckDuckGo, CachedCookieSessionsMixin):
    BASE_URL = 'http://tamilrockers.gr'
    OTHER_URLS = ['http://tamilrockers.tw', 'http://tamilrockers.tf', 'http://tamilrockers.pt', 'http://tamilrockers.ax', 'http://tamilrockers.tv', 'http://tamilrockers.fi','http://tamilrockers.re', 'http://tamilrockers.nz', 'http://tamilrockers.at',
                  'http://tamilrockers.nu', 'http://tamilrockers.lv', 'http://tamilrockers.ac',
                  'http://tamilrockers.cz', 'http://tamilrockers.mx']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ScraperBase.SCRAPER_TYPE_P2P, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    #REQUIRES_WEBDRIVER = True#('parse', )
    #WEBDRIVER_TYPE = 'phantomjs'

    def setup(self):
        super(TamilrockersAc, self).setup()
        self._request_connect_timeout = 600
        self._request_response_timeout = 600
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def get(self, url, **kwargs):
        return super(TamilrockersAc, self).get(url, allowed_errors_codes=[520, 522, 524], **kwargs)

    def _fetch_no_results_text(self):
        return u'No Results'

    def parse(self, parse_url, **extra):
        self.load_session_cookies()
        soup = self.get_soup(parse_url)

        if 'enable javascript' in unicode(soup):
            self._load_js_cookies(parse_url)
            soup = self.get_soup(parse_url)

        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('a strong')
        if title:
            for pre in soup.select('pre[class="prettyprint lang-"]'):

                for link in self.util.find_urls_in_text(pre.text):
                    self.log.debug(link)
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url= link,
                        link_title=title.text,
                    )

            magnet = soup.select_one('a[href*="magnet"]')
            if magnet:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=magnet['href'],
                    link_title=title,
                )


    def _load_js_cookies(self, url):
        self.load_session_cookies()
        self.webdriver().get(url)
        cookies = []
        for cookie in self.webdriver().get_cookies():
            self.log.debug(cookie)
            if 'sucuri' in cookie['name'] :
                self.http_session().cookies.set(cookie['name'], cookie['value'])
        self.save_session_cookies()
