# coding=utf-8
import time

from sandcrawler.scraper import SimpleScraperBase, ScraperBase, ScraperAuthException
from sandcrawler.scraper import CachedCookieSessionsMixin

class ViewingVault(CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = "http://www.viewingvault.com/forum"
    REGISTER_URL = "http://www.viewingvault.com"

    EMAIL = 'DawnJZiemba@dayrep.com'
    PASSW = 'itohl7Aongie9'
    LOGIN = 'nowles1'

    SINGLE_RESULTS_PAGE = True

    LONG_SEARCH_RESULT_KEYWORD = 'man'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(self.MEDIA_TYPE_FILM)
        self.register_media(self.MEDIA_TYPE_TV)
        self.register_media(self.MEDIA_TYPE_BOOK)
        self.register_media(self.MEDIA_TYPE_OTHER)

        self.register_url(self.URL_TYPE_SEARCH, self.REGISTER_URL)
        self.register_url(self.URL_TYPE_LISTING, self.REGISTER_URL)
        self._request_connect_timeout = 400
        self._request_response_timeout = 400

    def _login(self):
        """
        Either perform a login action, OR load our login cookies from a previous
        login.
        """
        self.load_session_cookies()

        page_response = self.get('{}/'.format(self.BASE_URL), allowed_errors_codes=[403, 410,])
        # check for a logout link.  This should flag for every case...
        if './ucp.php?mode=logout' not in page_response.text:
            self.log.info('Login box found - logging in.')
            # we need to do the login.
            response = self.post(self.BASE_URL + '/ucp.php?mode=login', data=dict(
                username=self.LOGIN, password=self.PASSW, autologin='on', login='Login'
            ))
            #if './ucp.php?mode=logout' not in response.text:
            #    raise ScraperAuthException('Invalid login.')

            self.save_session_cookies()

    def _fetch_search_url(self, search_term, media_type):
        self._login()
        # self.get(self.BASE_URL + '/search.php')
        return self.BASE_URL + '/search.php?keywords={}'.format(
            self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u' No suitable matches were found.'

    def _parse_search_result_page(self, soup):
        results = soup.select("div.postbody-header h3 a")
        if not results:
            self.submit_search_no_results()

        for result in results:
            self.submit_search_result(link_title=result.text,
                                      link_url=self.BASE_URL + result.get('href')[1:])

    def _fetch_next_button(self, soup):
        next = soup.select_one('.next.padding-h-5px > a')
        self.log.debug('---------------')
        return self.BASE_URL + next['href'][1:] if next else None

    def parse(self, parse_url, **extra):
        self._login()

        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        time.sleep(20)
        self.load_session_cookies()
        title = soup.select_one('#page-body h2').text.strip()
        series_season, series_episode = self.util.extract_season_episode(title)

        for code_box in soup.select('.codebox dd code'):

            text = str(code_box).replace('<br/>', ' ')

            for url in self.util.find_urls_in_text(text):
                if url.startswith('http') and not url.startswith(self.BASE_URL):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=url,
                                             link_title=title,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )

        for link in soup.select('.postlink'):
            if not link.href.startswith(self.BASE_URL):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )
