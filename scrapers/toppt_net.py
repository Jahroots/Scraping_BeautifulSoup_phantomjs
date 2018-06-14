# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class TopptNet(SimpleScraperBase):
    BASE_URL = 'http://warezplay.com'
    OTHERS_URLS = ['http://toppt.net']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    SINGLE_RESULTS_PAGE = True


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Sorry, but nothing matched your search criteria'

    def _fetch_next_button(self, soup):
        next_link = soup.select_one('a[class="next page-numbers"]')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):


        results = soup.select('#content h2.title a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )



    def _parse_parse_page(self, soup):
        title = soup.select_one('h2[class="title"]').text
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('span[data-mfp-src]'):
            movie_link = link['data-mfp-src']


            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )