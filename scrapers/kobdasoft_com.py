# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin

class KobdasoftCom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://kobdasoft.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    USERNAME = 'Howl1939'
    PASSWORD = 'ca7Cu9aej'
    EMAIL = 'kennethtroberts@dayrep.com'

    def _fetch_no_results_text(self):
        return u'The search did not return any results.'

    def _fetch_next_button(self, soup):
        return None

    def login(self):
        soup = self.post(self.BASE_URL, data = {'login_name' : self.USERNAME, 'login_password' : self.PASSWORD, 'login' : 'submit'})



    def _parse_search_result_page(self, soup):
        for result in soup.select('#main div.sitenews'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        self.login()

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
            title = title.text
        for link in soup.select('a[href*="/engine/go.php"]'):
            soup = self.get_soup(self.BASE_URL + link.href)
            for url in self.util.find_urls_in_text(soup.title.text):

                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url,
                    link_title=title,
                    series_season=series_season,
                    series_episode=series_episode,
                )
