# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmIndirGenTr(SimpleScraperBase):
    BASE_URL = 'http://www.filmindirgen.com'
    OTHERS_URLS = ['http://www.filmindir.biz', 'http://www.filmindir.gen.tr']

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'tur'
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        soup = self.get_soup(
            self.BASE_URL + '/?cat=0&s={}'.format(self.util.quote(search_term)),
        )

        results = soup.select('div.film a[data-wpel-link]')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_text=result['title'],
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        for link in soup.select('a[data-wpel-link="external"]'):
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=link['href'],
                                     link_title=link.text,
                                     )
