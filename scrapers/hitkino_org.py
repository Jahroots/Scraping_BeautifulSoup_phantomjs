# coding=utf-8
import base64
from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class HitkinoOrg(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://hitkino.org'
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self.bunch_size = 20
        self.showposts = 1

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('span.ntitle'):
            link = result.select_one('a')
            if link:
                if '/#' in link.href:
                    continue
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    )
                found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.news a'):
            if 'go.php?url=' in link.href:
                link_url = self.get_redirect_location(link.href)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link_url,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
