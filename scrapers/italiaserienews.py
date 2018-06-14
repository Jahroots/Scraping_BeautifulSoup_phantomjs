# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin

class ItaliaserieNews(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://www.serietvu.online'
    OTHER_URLS = ['http://www.serietvu.online', 'http://www.serietvu.com', 'http://www.italiaserie.news', 'http://www.italiaserie.click']

    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'

    def setup(self):
        super(ItaliaserieNews, self).setup()
        self._request_response_timeout = 500
        self._request_connect_timeout = 500

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"Risultati della ricerca per"

    def _parse_search_results(self, soup):
        found = 0
        for results in soup.select('div.item a'):
            result = results['href']
            if result:
                title = results.text.strip()
                self.submit_search_result(
                    link_url=result,
                    link_title=title,
                )
                found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):

        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div.item a[data-href]')
        for result in results:
            movie_link = result['data-href']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )


