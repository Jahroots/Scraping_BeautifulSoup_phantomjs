# coding=utf-8

import re
import json
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin
from sandcrawler.scraper import SimpleScraperBase, ScraperBase


class CasaCinemaBZ(CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'https://cb-01.net'
    OTHER_URLS = ['https://cb-01.eu']

    LOADED = False
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "ita"

        self.register_media(SimpleScraperBase.MEDIA_TYPE_FILM)
        self.register_media(SimpleScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_next_button(self, soup):
        link = soup.select_one('a[class="next page-numbers"]')
        if link:
            return link.href
        else:
            return None


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term.encode('utf-8'))

    def get(self, url, **kwargs):
        return super(CasaCinemaBZ, self).get(url, allowed_errors_codes=[503, ], **kwargs)

    def search(self, search_term, media_type, **extra):
        if not self.LOADED:
            self._load_js_cookies()
            self.LOADED = True

        search_url = self._fetch_search_url(search_term, media_type)
        soup = self.get_soup(search_url)
        self._parse_search_results(soup)


    def _parse_search_results(self, soup):
        # no flag for no results... just check for a lack of them.
        results = soup.select('.titleFilm a')
        if not results:
            return self.submit_search_no_results()
        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip(),
            )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_results(soup)

    def _parse_series_page(self, soup):
        # Grab each season link, open it, and grab episode links within.
        for season_link in soup.select('ul.sezon-list a'):
            season_soup = self.get_soup(season_link['href'])
            for episode_link in season_soup.select('div.list-episodes a'):
                if episode_link['href'].startswith('javascript:'):
                    continue
                self.submit_search_result(
                    link_url=episode_link['href'],
                    link_title=episode_link.text
                )

    def replace_all(self, encoded_text,  d):
        for k, v in d.items():
            key_num = '&%s;' % k
            value_char = v.strip('"')
            rx = re.compile('{}'.format(key_num))
            encoded_text = rx.sub('{}'.format(value_char), encoded_text)
        return encoded_text

    def parse(self, parse_url, **extra):
        self.load_session_cookies()
        soup = self.get_soup(parse_url)
        iframes = soup.select('div.videodet iframe')
        title = soup.select_one('.videopart h1').text.strip()
        for iframe in iframes:
            src = iframe['src']
            if 'http' not  in src:
                src = 'http:' + src
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                 link_url=src,
                                 link_title=title,
                                 )


    


    def _load_js_cookies(self):
        self.load_session_cookies()
        #self.webdriver().get(url)
        cookies = []
        for cookie in self.webdriver().get_cookies():
            self.log.debug(cookie)
            self.http_session().cookies.set(cookie['name'], cookie['value'])
        self.save_session_cookies()
