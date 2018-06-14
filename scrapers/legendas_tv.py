# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class LegendasTv(SimpleScraperBase):
    BASE_URL = 'http://legendas.tv'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    USER_NAME = 'Youncle'
    PASSWORD = '12345.'
    EMAIL = 'davisbnorrell@armyspy.com'

    def setup(self):

        super(self.__class__, self).setup()
        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = ('search', )


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/busca/{}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.load_more')
        if next_button:
            return self.BASE_URL + next_button.href
        return None


    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self.BASE_URL + '/login', data = {'_method' : 'POST',
                                                                 'data[User][username]' : self.USER_NAME,
                                                                  'data[User][password]' : self.PASSWORD}
                    )


        self.webdriver().get(self._fetch_search_url(search_term, media_type))
        soup = self.make_soup(self.webdriver().page_source)


        results = soup.select('#resultado_busca p a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)


    def _parse_search_result_page(self, soup):

        for result in soup.select('#resultado_busca p'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text.strip(),
                image=self.util.find_image_src_or_none(result, 'img'),
            )


            next_button = self._fetch_next_button(soup)
            if next_button and self.can_fetch_next():
                soup = self.get_soup(next_button)
                self._parse_search_result_page(soup)

    def parse(self, parse_url, **extra):
        self.post_soup(self.BASE_URL + '/login', data={'_method': 'POST',
                                                       'data[User][username]': self.USER_NAME,
                                                       'data[User][password]': self.PASSWORD}
                       )
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('section h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        link =  soup.select_one('section button.icon_arrow')
        if link and link['onclick']:
            self.log.debug(link)
            link = self.BASE_URL + link['onclick'].replace("window.open('", '').replace(", '_self')", '')
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_title=title.text.strip(),
                series_season=series_season,
                series_episode=series_episode,
            )
