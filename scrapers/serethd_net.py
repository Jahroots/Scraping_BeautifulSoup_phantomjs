# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CachedCookieSessionsMixin, CloudFlareDDOSProtectionMixin

class SerethdNet(CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin,SimpleScraperBase):
    BASE_URL = 'https://serethd.net'
    OTHER_URLS = ['http://serethd.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'heb'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        super(self.__class__, self).setup()
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'


    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None


    def get_soup(self, url, **kwargs):
        # If the soup size is a specific length, it means it's their
        # blocker - load up webdriver and get past that.
        soup = super(SerethdNet, self).get_soup(url, **kwargs)
        if len(soup.text) == 2470:
            self._load_js_cookies(url)
            soup = self.get_soup(url)
        return soup

    def search(self, search_term, media_type, **extra):
        search_url = self._fetch_search_url(search_term, media_type)
        self.load_session_cookies()
        soup = self.get_soup(search_url)
        self._parse_search_result_page(soup)


    def _parse_search_result_page(self, soup):
        results = soup.select('a[class="ml-mask jt"]')
        if not results or len(results) == 0:
            return self.submit_search_no_results()
        for result in soup.select('a[class="ml-mask jt"]'):
            link = result.href
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
            )


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.desc p a'):
            if not link.href.startswith(self.BASE_URL):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                )
        for iframe in soup.select('iframe'):
            if iframe['src']:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe['src']
                )

    def _load_js_cookies(self, url):
        self.load_session_cookies()
        self.webdriver().get(url)
        cookies = []
        for cookie in self.webdriver().get_cookies():
            self.log.debug(cookie)
            if 'prog_protects' in cookie['name']:
                self.http_session().cookies.set(cookie['name'], cookie['value'])
        self.save_session_cookies()