# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class GetyarnIo(SimpleScraperBase):
    BASE_URL = 'https://getyarn.io'
    OTHER_URLS = ['http://getyarn.io']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        super(GetyarnIo, self).setup()
        self._request_connect_timeout = 300
        self._request_response_timeout = 300

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/yarn-find?text={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No Clips Found For'

    def _fetch_next_button(self, soup):
        return None


    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('div.clips-columns a'):
            result = self.BASE_URL+results['href']
            title = results.find('div', 'title')
            if title:
                title = title.text

            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('a.yarn-link').text.strip()
        index_page_title = self.util.get_page_title(soup)
        for results in soup.select('source.realsource'):
            movie_link = results['src']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )


    def get(self, url, **kwargs):
        return super(GetyarnIo, self).get(url, allowed_errors_codes=[404], **kwargs)