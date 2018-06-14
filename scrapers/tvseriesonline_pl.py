# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class TvseriesonlinePl(SimpleScraperBase):
    BASE_URL = 'http://www.tvseriesonline.pl'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'pol'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Website no longer exists.')

    def search(self, search_term, media_type, **extra):
        search_regex = self.util.search_term_to_search_regex(search_term)
        results = False
        main_page = self.get_soup(self.BASE_URL)
        for link in main_page.select('ul#categories a'):
            if search_regex.search(link.text):
                series_soup = self.get_soup(
                    link.href
                )
                for link in series_soup.select('div.post h4.title a'):
                    results = True
                    self.submit_search_result(
                        link_url=link.href,
                        link_title=link.text,
                    )

        if not results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.video-links a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
