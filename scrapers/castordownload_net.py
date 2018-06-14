# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class CastordownloadNet(SimpleScraperBase):
    BASE_URL = 'http://www.castordownload.org'
    OTHER_URLS = ['http://www.castordownload.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_P2P, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    page = 1
    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Encontramos 0 post relacionado à sua pesquisa'

    def search(self, search_term, media_type, **extra):
        self.page = 1
        super(self.__class__, self).search(search_term, media_type, **extra)

    def _fetch_next_button(self, soup):
        self.page += 1
        next_button = soup.find('a', text=str(self.page))
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):

        results = soup.select('div.content-post h2 a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('a[href*="magnet"]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
