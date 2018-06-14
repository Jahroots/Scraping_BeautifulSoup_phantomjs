# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class WawaManiaBiz(SimpleScraperBase):
    BASE_URL = 'http://wawa-mania.biz'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_GAME, ]
    WEBDRIVER_TYPE = 'phantomjs'
    REQUIRES_WEBDRIVER = True
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        super(WawaManiaBiz, self).setup()
        self._request_connect_timeout = 500
        self._request_response_timeout = 500

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term.encode('utf-8'))

    def _fetch_no_results_text(self):
        return u'Not Found'

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        search_url = self._fetch_search_url(search_term, media_type)
        self.webdriver().get(search_url)

        soup = self.make_soup(self.webdriver().page_source)

        results = soup.select('div.minipost a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)
        self.webdriver().close()

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.minipost'):
            link = result.select_one('a')
            if result:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def parse(self, parse_url, **extra):
        self.webdriver().get(parse_url)
        soup = self.make_soup(self.webdriver().page_source)
        self._parse_parse_page(soup)
        self.webdriver().close()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.post center a'):
            if 'HOMEPAGE' in link.text or 'NFO' in link.text or 'Torrent Search' in link.text:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
