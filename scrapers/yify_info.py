# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin


class Yify_info(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://yify.info'
    OTHER_URLS = []

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 20
        self.media_type_to_category = 'film 0, tv 0'
        # self.encode_search_term_to = 'cp1251'
        self.showposts = 1

    def _parse_search_result_page(self, soup):
        for result in soup.select('.line a'):
            self.submit_search_result(
                link_url=result['href'].lower(),
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.post-title').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.text2 a'):
            self.submit_parse_result(
                index_page_title=soup.title.text.strip(),
                link_url=self.get_soup(self.BASE_URL + link.href).select_one('a#page').href,
                link_title=title,
                series_season=season,
                series_episode=episode
            )
