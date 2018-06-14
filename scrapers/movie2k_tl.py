# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Movie2KTl(SimpleScraperBase):
    BASE_URL = 'http://www.movie2k.sh'
    OTHER_URLS = ['http://www.movie2k.am', 'http://www.movie2k.ac']
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "deu"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        # XXX Says they host TV, but can't find any via search.
        # self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL,]:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.get_soup(
                self.BASE_URL + '/search/' + search_term,
            )

        )

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('a.coverImage')
        if not results:
            self.submit_search_no_results()

        for result in results:
            main_link = result.find('a')  # first link.

            video_link = result
            self.submit_search_result(
                    link_url=video_link['href'],
                    link_title=result.text,
                )

    def _parse_parse_page(self, soup):
        # Find the click link image, and what it links to.
        for result in soup.select('table.dataTable td.sourceNameCell a'):

            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url=result['href'],
                link_text = result.text
            )
