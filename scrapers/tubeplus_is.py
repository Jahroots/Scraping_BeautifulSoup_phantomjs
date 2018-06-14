# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class TubePlusIsFilm(CloudFlareDDOSProtectionMixin,SimpleScraperBase):
    BASE_URL = 'https://tvbox.ag'
    OTHER_URLS = ['http://www.tubeplus.ag', 'http://www.tubeplus.me', 'http://www.tubeplus.is']
    SINGLE_RESULTS_PAGE = True


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL,] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'


    def get(self, url, **kwargs):
        # Site does a cookie check,
        self._http_session.cookies.set(
            'check',
            '2',
            domain='tvbox.ag')
        return super(TubePlusIsFilm, self).get(url, **kwargs)

    def _fetch_no_results_text(self):
        return 'No Matches.'

    def _fetch_next_button(self, soup):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search?q=' + self.util.quote(search_term)

    def _parse_search_result_page(self, soup):
        results = soup.select('div.result')
        if not results:
            self.submit_search_no_results()

        for result in results:
            result = result.select_one('a')
            self._handle_search_result(result)

    def _handle_search_result(self, result):
        # Just submit our film link.
        self.submit_search_result(
            link_url=self.BASE_URL + result['href'],
            link_title=result.text,
            image=self.BASE_URL + self.util.find_image_src_or_none(result, 'img'),
        )


    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        tr = soup.select('table.show_links tr a[onclick]')
        for onclick in tr:
            onclick = onclick['onclick'].replace("report('", '').split("',")[0].strip()
            if 'http' in onclick:
                self.submit_parse_result(index_page_title= self.util.get_page_title(soup),
                                         link_url=onclick,
                                         link_title=soup.select_one('div h1').text
                                         )



