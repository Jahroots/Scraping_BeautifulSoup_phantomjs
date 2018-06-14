# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class WatchonlineSeriesCom(SimpleScraperBase):
    BASE_URL = 'http://watchourseries.com'
    OTHER_URLS = ['http://watchonline-series.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    SINGLE_RESULTS_PAGE = True

    def _fetch_search_url(self, search_term, media_type):
        return 

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self.BASE_URL + '/search.html', data = {'key' : search_term})

        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        results = soup.select('ul.listings li a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in soup.select('ul.listings li'):
            link = result.select_one('a')

            soup = self.get_soup(self.BASE_URL + link.href)
            episodes = soup.select('ul li[itemprop="episode"] a')
            for ep in episodes:
                self.submit_search_result(
                    link_url=self.BASE_URL + ep.href,
                    link_title=ep.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        results = soup.select('span a.buttonlink')
        for result in results:
            soup = self.get_soup(self.BASE_URL + result.href)

            for link in soup.select('div a[class="btnlarge blue"]'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
