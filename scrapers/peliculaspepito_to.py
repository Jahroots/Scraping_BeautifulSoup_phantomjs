#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import DuckDuckGo, SimpleScraperBase


class PeliculasPepitoTo(DuckDuckGo, SimpleScraperBase):

    BASE_URL = 'http://www.peliculaspepito.to'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Website with not useful information')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)



    def get(self, url, **kwargs):
        return super(PeliculasPepitoTo, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def _parse_parse_page(self, soup):
            for link in soup.find_all('a', 'btn btn-mini enlace_link'):
                if not link['href']:
                    continue
                if 'peliculaspepito.to/s/ngo' not in link['href']:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=link['href'],
                                             asset_type=ScraperBase.MEDIA_TYPE_FILM
                                             )
                else:
                    parse_soup = self.get_soup(link['href'])
                    movie_link = parse_soup.find('a', 'btn btn-mini enlace_link')
                    if movie_link['href']:
                        self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                 link_url=movie_link['href'],
                                                 asset_type=ScraperBase.MEDIA_TYPE_FILM
                                                 )

