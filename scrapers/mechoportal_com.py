# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin, CloudFlareDDOSProtectionMixin, ScraperAuthException

class MechoportalCom(CloudFlareDDOSProtectionMixin, OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.mechoportal.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'en'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = 'star wars'

    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'

    USERNAME = 'zeppler1981'
    PASSWORD = 'IlSp.2010'

    def _login(self):
        # If we're already logged in, don't worry about.
        response = self.get(self.BASE_URL)
        if self.USERNAME in response.text:
            return
        response = self.post(
            self.BASE_URL,
            data={
                'login_name': self.USERNAME,
                'login_password': self.PASSWORD,
                'Submit': '',
                'login': 'submit',
            }
        )
        if self.USERNAME not in response.text:
            raise ScraperAuthException('Invalid username')
        return

    def _fetch_search_url(self, search_term):
        return self.BASE_URL

    def _include_xy_in_search(self):
        return False

    def search(self, search_term, media_type, **extra):
        self._login()
        super(MechoportalCom, self).search(search_term, media_type, **extra)

    def _fetch_no_results_text(self):
        return u'site search yielded no results.'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.mlink div.lcol h2 a'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
            )

    def parse(self, parse_url, **extra):
        self._login()
        return super(MechoportalCom, self).parse(parse_url, **extra)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)

        for link in self.util.find_urls_in_text(str(soup.select_one('div.maincont') or '')):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
            )
