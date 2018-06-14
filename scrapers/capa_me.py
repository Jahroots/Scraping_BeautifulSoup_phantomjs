# coding=utf-8
import base64

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class CapaMe(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = "http://www.capa.me"

    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = u'ìåãàí'


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 400
        self.media_type_to_category = 'film 26, tv 46'
        self.encode_search_term_to = 'cp1251'
        self.showposts = 0

    def _fetch_no_results_text(self):
        return u'поиск по сайту не дал никаких результатов'

    def _parse_search_result_page(self, soup):
        for result in soup.select(".newsbody p a"):
            self.submit_search_result(link_title=result.parent.parent.select_one('img').get('title'),
                                      link_url=result.get('href'))

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Далее »')
        return link['href'] if link else None

    def _parse_parse_page(self, soup):
        title = soup.title.text
        for link in soup.select('.quote noindex a'):
            if link['href'].startswith('/link/'):
                # /link/?a%3Ahttp%3A%2F%2Fnitroflare.com%2Fview%2F08A61883B95C712%2FThe.Hateful.Eight.2015.1080p.BluRay.DTS.5xRus.Eng.mkv
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_title=title,
                    link_url=self.util.unquote(link['href'])[9:]
                )
            elif not link['href'].startswith('http://www.capa.me'):
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_title=title,
                    link_url=link['href'])

