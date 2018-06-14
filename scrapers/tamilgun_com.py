# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class TamilgunCom( SimpleScraperBase):
    BASE_URL = 'http://tamilgun.cool'
    OTHER_URLS = ['http://tamilgun.work', 'http://tamilgun.fun', 'http://tamilgun.ooo','http://tamilgun.pro', 'http://www.tamiltrend.com']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    ALLOW_FETCH_EXCEPTIONS = True


    def setup(self):
        super(TamilgunCom, self).setup()
        self._request_connect_timeout = 500
        self._request_response_timeout = 600

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"We have nothing on this"

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Next →')
        return self.BASE_URL + next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('h3 a'):
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url, allowed_errors_codes=[404, 403,])
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div.ts-video iframe')
        if results:
            for result in results:
                movie_link = result['src']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_text=title,
                )
        else:
            results = soup.select('div.video-container iframe')
            for result in results:
                movie_link = result['src']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_text=title,
                )

