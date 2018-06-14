# coding=utf-8

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Semelike(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.semelike.net'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"
        raise NotImplementedError('http://www.semelike.net is depricated')
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

        # OpenSearchMixin advanced search settings
        self.bunch_size = 200
        self.media_type_to_category = 'film 43, tv 52'
        # self.encode_search_term_to = 'cp1251'
        self.showposts = 1

    def _parse_search_result_page(self, soup):
        for result in soup.select('.dpad.searchitem h3 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('#news-title').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for lnk in soup.select('.quote a'):
            url = self.get_redirect_location(self.BASE_URL + lnk.href) if lnk.href.startswith(
                '/file/go.php') else lnk.href
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=url,
                                     link_title=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )
