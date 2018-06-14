# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import re
class VkoolNet(SimpleScraperBase):
    BASE_URL = 'http://vkool.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    USER_NAME = 'Knevity'
    PASSWORD = 'ooNg9oon'
    EMAIL = 'MitchellAAdair@rhyta.com'
    PAGE = 1
    LAST = 0
    SEARCH_URL = ''
    USER_AGENT_MOBILE = False

    def _fetch_search_url(self, search_term, media_type):
        self.SEARCH_URL = self.BASE_URL + '/search/' + self.util.quote(search_term)
        return self.SEARCH_URL

    def _fetch_no_results_text(self):
        return u'Không tìm thấy kết quả với từ khóa'

    def _fetch_next_button(self, soup):
        self.PAGE += 1
        if self.PAGE <= self.LAST:
            return self.SEARCH_URL+'/' + str(self.PAGE) + '.html'
        else:
            return None

    def search(self, search_term, media_type, **extra):
        self.LAST = 0
        self.PAGE = 1
        soup = self.get_soup(self._fetch_search_url(search_term, media_type))
        a = soup.find('a', text = 'LAST →')

        if self._fetch_no_results_text() in unicode(soup):
            return self.submit_search_no_results()

        if a:
            self.LAST = int(re.findall(r'\d+', a['href'])[0])

        self._parse_search_result_page(soup)


    def _parse_search_result_page(self, soup):
        for result in soup.select('ul.list-movie li.movie-item'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

            next_button = self._fetch_next_button(soup)
            if next_button and self.can_fetch_next():
                soup = self.get_soup(next_button)
                self._parse_search_result_page(soup)

    def _parse_parse_page(self, soup):

        a = soup.select_one('#btn-film-watch')['href']
        self.log.debug(a)
        soup = self.get_soup(a)

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('a[data-ep]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=self.BASE_URL + '/' + link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
