# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, \
    CachedCookieSessionsMixin, OpenSearchMixin, ScraperAuthException

class ExsitesPl(OpenSearchMixin, CachedCookieSessionsMixin, SimpleScraperBase):

    BASE_URL = 'http://exsites.pl'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'pol'
    MEDIA_TYPES = [
        ScraperBase.MEDIA_TYPE_FILM,
        ScraperBase.MEDIA_TYPE_TV,
        ScraperBase.MEDIA_TYPE_GAME,
        ScraperBase.MEDIA_TYPE_OTHER,
    ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    USERNAME = u'Postra'
    PASSWORD = u'eiwei4eeroJai'

    def login(self):
        self.load_session_cookies()
        response = self.get(self.BASE_URL)
        # Logout!
        if u'Wyloguj!' not in response.text:
            # do the login.
            response = self.post(
                self.BASE_URL,
                data={
                    'login_name': self.USERNAME,
                    'login_password': self.PASSWORD,
                    'x': 12,
                    'y': 18,
                    'login': 'submit',
                }
            )
            if u'Wyloguj!' not in response.text:
                raise ScraperAuthException('Failed login')
            else:
                self.save_session_cookies()
        return

    def _fetch_search_url(self, search_term):
        return self.BASE_URL

    def search(self, search_term, media_type, **extra):
        self.login()
        super(ExsitesPl, self).search(search_term, media_type, **extra)

    def _parse_search_result_page(self, soup):
        results = soup.select('div.base div.bshead h1 a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for link in results:
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
            )

    def parse(self, parse_url, **extra):
        self.login()
        super(ExsitesPl, self).parse(parse_url, **extra)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        body = soup.select_one('div.maincont')
        for link in self.util.find_urls_in_text(unicode(body)):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                series_season=series_season,
                series_episode=series_episode,
            )
