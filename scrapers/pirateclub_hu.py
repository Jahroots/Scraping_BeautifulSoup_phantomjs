# coding=utf-8

from sandcrawler.scraper import \
    ScraperBase, \
    SimpleScraperBase, \
    CachedCookieSessionsMixin, \
    ScraperAuthException, \
    ScraperFetchException, CloudFlareDDOSProtectionMixin
from time import sleep
from sandcrawler.scraper.caching import cacheable

class PirateclubHu(CachedCookieSessionsMixin, CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://www.pirateclub.hu'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'hun'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USER_NAME ='Mothre1937'
    PASSWORD = 'ohM9yahQu'
    EMAIL = 'SusanaVPaolucci@dayrep.com'
    FIRST = True
    LONG_SEARCH_RESULT_KEYWORD = '2016'

    USER_AGENT_MOBILE = False

    def setup(self):
        super(PirateclubHu, self).setup()
        self._request_connect_timeout = 300
        self._request_response_timeout = 600
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?app=core&module=search&do=search&fromMainBar=1'

    def _fetch_no_results_text(self):
        return u'Nincs eredmény a következő kulcsszóra'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('li.next a')
        if next_button:
            return next_button.href
        return None

    def do_search(self, search_url, search_term):
        return self.post_soup(
            search_url,
            data={
                'search_term': search_term,
                'search_app': 'forums'
            },
            allowed_errors_codes=[403, 404, ]
        )

    def search(self, search_term, media_type, **extra):
        self.page = 1

        self.load_session_cookies()

        # Attempt to search.
        soup = self.do_search(
            self._fetch_search_url(search_term, media_type),
            search_term
        )

        # You do not have permission to use the search system.
        if u'Nincs jogosultságod használni a kereső rendszert.' in unicode(soup):
            self.login()
            soup = self.do_search(
                self._fetch_search_url(
                    search_term, media_type),
                search_term
            )


        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        results = soup.select('td h4 a')
        if (not results and len(results) == 0) and self.page == 1:
            return self.submit_search_no_results()

        for result in soup.select('td h4'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

        next_button = self._fetch_next_button(soup)

        if next_button and self.can_fetch_next():
            self.page += 1
            self.log.debug('________________________')
            try:
                soup = self.get_soup(next_button)
            except Exception as e:
                self.login()
                soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)


    def parse(self, parse_url, **extra):
        self.load_session_cookies()
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        pre = soup.select_one('pre[class*="prettyprint"]')

        if pre and pre.text:
            pre = pre.text

            links = self.util.find_urls_in_text(pre)
            for link in links:
                self.log.debug(link)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=title.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

    def login(self):
        soup = self.get_soup(self.BASE_URL)
        key = soup.select_one('input[name="auth_key"]')['value']
        ref = soup.select_one('input[name="referer"]')['value']

        response = self.post(
            u'{}/index.php?app=core&module=global&section=login&do=process'.format(self.BASE_URL),
            data={'auth_key': key,
                  'referer': ref,
                  'ips_username': self.USER_NAME,
                  'ips_password': self.PASSWORD,
                  'rememberMe': 1
                  }
        )
        # Check for a successful login page
       # if u'Sikeres bejelentkez' not in response.text:
        #    raise ScraperAuthException(
        #        'Failed login with %s / %s' % (self.USER_NAME, self.PASSWORD))

        # If so - save these cookies for later.
        self.save_session_cookies()
