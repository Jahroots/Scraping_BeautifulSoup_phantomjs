# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class NeomaksRu(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://neomaks.ru'
    OTHER_URLS = ['http://neomaks.ru']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ]:  # + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 400
        self.media_type_to_category = 'film 2, tv 29'
        self.encode_search_term_to = 'cp1251'
        self.showposts = 0

    def _parse_search_result_page(self, soup):
        for result in soup.select(".news_cont h2 a"):
            self.submit_search_result(link_title=result.text,
                                      link_url=result.get('href'))

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Далее')
        return link['href'] if link else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('.news_cont > h2').text
        for link in soup.select('#dle-content .quote a'):
            self.log.debug(link.href)
            if 'http' in link.href and not link['href'].startswith(self.BASE_URL):
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_title=title,
                    link_url=link.href.encode('ascii', 'ignore').decode('ascii'),
                    )
