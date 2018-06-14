# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class VeziserialeonlineInfo(SimpleScraperBase):
    BASE_URL = 'http://www.veziseriale.online'
    OTHER_URLS = ['http://www.veziserialeonline.info']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_FILM]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        super(VeziserialeonlineInfo, self).setup()
        # Hah - search page is 5MB for 'man'
        self._request_size_limit = (1024 * 1024 * 10)  # Bytes
        #self._request_response_timeout = 600
        #self._request_connect_timeout = 300

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php'

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self._fetch_search_url(search_term, media_type), data={'menu': 'search',
                                                                                     'search': 'Search',
                                                                                     'query': search_term})
        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        found_results = False
        for result in soup.select('li.hentry'):
            found_results = True
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

        for result in soup.select('div.movieline'):
            found_results = True
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

        if not found_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        # assert_center = soup.select('center')
        for iframe in soup.select('iframe'):
            if 'facebook' in iframe['src']:
                continue
            url = iframe['src']
            if 'http' not in url:
                url = 'http:' + url

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url= url

            )
