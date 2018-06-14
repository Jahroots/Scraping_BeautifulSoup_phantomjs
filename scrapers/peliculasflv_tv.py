# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PeliculasflvTv(SimpleScraperBase):
    BASE_URL = 'https://www.peliculasflv.tv'
    LONG_SEARCH_RESULT_KEYWORD = 'super'


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Lo sentimos, no hay películas que correspondan a sus criterios'

    def _fetch_next_button(self, soup):
        next_link=''
        try:
            next_link = soup.find('a', text=u'Siguiente »')['href']
        except TypeError:
            pass
        return next_link if next_link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('h3 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.single-title').text
        index_page_title = self.util.get_page_title(soup)
        for url in soup.select('iframe'):
            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=url['src'],
                                     link_title=title
                                     )
