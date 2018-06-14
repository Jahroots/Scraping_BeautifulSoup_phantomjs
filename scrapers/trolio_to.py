# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class TrolioTo(SimpleScraperBase):
    BASE_URL = 'http://trolio.to'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Deprecated, Website timeout.')

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/cauta/?q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class="movie_w tal"] div a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('a[iframe]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['iframe'],
                link_title=link.text,
            )