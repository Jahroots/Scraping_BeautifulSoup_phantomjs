# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class MaxipelisNet(SimpleScraperBase):
    BASE_URL = 'http://cinematas.com'
    OTHER_URLS = ['http://www.maxipelis.tv', 'http://www.maxipelis.net']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    #LONG_SEARCH_RESULT_KEYWORD = '2015'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    SINGLE_RESULTS_PAGE = True

    def _fetch_search_url(self, search_term, media_type=None):
        return u'{}/?s={}'.format(self.BASE_URL, search_term)

    def _fetch_no_results_text(self):
        return 'Sorry, but nothing matched your search terms'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        rslts = soup.select('article h2.entry-title a')

        for result in rslts:
            link = result['href']
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        index_page_title = self.util.get_page_title(soup),
        for link in soup.select('iframe[allowfullscreen]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_title=title,
                link_url=link['src']
            )

