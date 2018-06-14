# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class AllYouLike(SimpleScraperBase):
    BASE_URL = 'http://www.allyoulike.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Nothing Found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for link in soup.select('#content ul li strong a'):
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text)

    def _parse_parse_page(self, soup):
        title = soup.select_one('.title h2').text.strip()
        series_season, series_episode = self.util.extract_season_episode(title)

        for dl in soup.select('.entry p strong a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=dl['href'],
                                     link_text=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )
