# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class CouchTunerCh(SimpleScraperBase):
    BASE_URL = 'http://couch-tuner.ch'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Deprecated. Links provided from projectfree-tv.org')

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search/?free={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.entry ul li'):
            link = result.select_one('a')
            season_soup = self.get_soup(self.BASE_URL+link.href)
            for season_links in season_soup.select('div.entry ul li'):
                season_link = season_links.select_one('a')
                self.submit_search_result(
                    link_url=season_link.href,
                    link_title=season_link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('a.buttonlink'):
            movie_soup = self.get_soup(self.BASE_URL+link['href'])
            for movie_link in movie_soup.select('div.entry iframe'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link['src'],
                    link_title=movie_link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
