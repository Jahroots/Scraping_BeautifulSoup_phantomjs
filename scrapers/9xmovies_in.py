# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class NineXmovies(SimpleScraperBase):
    BASE_URL = 'https://9xmovies.org'
    OTHER_URLS = ['https://9xmovies.info', 'https://9xmovies.to','https://9xmovies.net', 'https://9xmovies.in']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'hin'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return '404 Not found'

    def _fetch_next_button(self, soup):
        link = soup.select_one('a[class="next page-numbers"]')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        any_results = False
        for result in soup.select('figure'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('main.page-body a'):
            if 'TORRENT' in link.text:
                continue
            self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link.href,
                        link_title=link.text,
                        series_season=series_season,
                        series_episode=series_episode
                    )
