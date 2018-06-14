# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class Myp30movie_Ir(SimpleScraperBase):
    BASE_URL = 'http://www.p30movies.co'
    OTHERS_URLS = ['http://www.myp30movies.ir', 'http://www.myp30movie.ir', 'http://www.p30movies.ir']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = False
        for results in soup.select('div.title h3 a'):
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            found = True
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div.contents a')
        for result in results:
            self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=result.href,
                    link_text=result.text,
                )