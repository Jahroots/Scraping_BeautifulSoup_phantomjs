#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.extras import SimpleScraperBase, WebdriverSessionExtractionMixin


class FiuxyCom(SimpleScraperBase):

    BASE_URL = 'https://fiuxy.me'
    OTHER_URLS = ['https://www.fiuxy.bz', 'https://www.fiuxy.co', 'https://www.fiuxy.net', ]

    TEST_URL = "http://www.fiuxy.com/link/?iwrchsmtvjshvrWccucR+B2NA446/vPMr3npyABODdk="

    TEST_RESULTS = ["http://adf.ly/wrWIE"]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                u'{}/search/search'.format(self.BASE_URL),
                data={
                    'keywords': search_term,
                    'users': '',
                    'date': '',
                    '_xfToken': '',
                }
            )
        )

    def _fetch_no_results_text(self):
        return u'No se encontraron resultados.'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u'Siguiente >')
        if next_button:
            return u'{}/{}'.format(self.BASE_URL, next_button.href)
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.titleText h3.title a')
        for link in results:
            self.submit_search_result(
                link_url=u'{}/{}'.format(self.BASE_URL, link.href),
                link_title=link.text,
            )

    def _parse_parse_page(self, soup):
        for link in self.util.find_urls_in_text(
                unicode(soup.select_one('div.messageContent'))
            ):
            if link.startswith('https://cdn.fiuxy.me/proxy.php?image='):
                link = self.util.unquote(
                    link[37:]
                )
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link,
            )

