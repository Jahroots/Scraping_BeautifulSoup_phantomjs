# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class EurostreamingVideo(SimpleScraperBase):
    BASE_URL = 'http://www.eurostreaming.video'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    SINGLE_RESULTS_PAGE = True
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/?s=' + self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        found=0
        for result in soup.select('div.container-index-post'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        link = soup.select_one('iframe.embed-responsive-item')
        if link:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
        movie_links = soup.select('a.green-link')
        for movie_link in movie_links:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link['newlink'],
                link_title=movie_link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
