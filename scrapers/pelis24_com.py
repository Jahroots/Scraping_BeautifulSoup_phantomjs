#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import OpenSearchMixin


class Pelis24Com(OpenSearchMixin, SimpleScraperBase):

    BASE_URL = 'https://pelis24.tv'
    OTHER_URLS = ['http://pelis24.com', 'http://pelis24.tv']

    def setup(self):
        raise NotImplementedError('Deprecated. Website no longer exists.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def _fetch_no_results_text(self):
        return u'Lamentablemente,, la búsqueda en el sitio no ha dado ningún resultado. '

    def _parse_search_result_page(self, soup):
        for result in soup.select('a[class="sres-wrap clearfix"]'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
                image=self.BASE_URL + self.util.find_image_src_or_none(result, 'img')
            )

    def _parse_parse_page(self, soup):
        self._parse_iframes(
            soup,
            css_selector='div.player-section iframe'
        )

