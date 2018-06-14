# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin


class Wawacity(CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'http://www.torrents9.org'
    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

        raise NotImplementedError('Website return just mostly torrent files. No relevent information')

    def _load_js_cookies(self, url):
        self.load_session_cookies()
        self.webdriver().get(url)
        cookies = []
        for cookie in self.webdriver().get_cookies():
            self.log.debug(cookie)
            self.http_session().cookies.set(cookie['name'], cookie['value'])
        self.save_session_cookies()

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search_torrent/'

    def _fetch_no_results_text(self):
        return u'Aucune fiches trouvées.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def search(self, search_term, media_type, **extra):
        self._load_js_cookies(self.BASE_URL)
        #post the search
        soup = ''
        try:
            self.post_soup(self._fetch_search_url(search_term, media_type), data = {'champ_recherche' : search_term})

        except Exception as e:
            self.log.debug(str(e))

        self.load_session_cookies()
        soup = self.get_soup(self._fetch_search_url(search_term, media_type) + '{}.html'.format(search_term), data = {'Referer' : 'http://www.torrents9.org/search_torrent/{}.html'.format(search_term)} )

    def _parse_search_result_page(self, soup):
        for result in soup.select('#searchResults .wa-sub-block-title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.wa-sub-block-title').text.strip()
        # sea, epi = self.util.extract_season_episode(full_title)

        for link in soup.select('.wa-post-link-list .link-row a'):
            href = link.get('href', '')
            if href.startswith('http') and 'wawacity' not in href:

                #try:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=href,
                                             link_title=title,
                                             # series_season=sea,
                                             # series_episode=epi
                                             )
                #except Exception as e:
                 #   self.log.exception(e)
