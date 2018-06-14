# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import DuckDuckGo, SimpleScraperBase


class AwesomeDl(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://awesomedl.ru'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        return super(AwesomeDl, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def _fetch_no_results_text(self):
        return u'The page you requested could not be found'

    def _parse_parse_page(self, soup, find_mirrors=True):
        title = ''
        try:
            title = soup.select_one('.content h2').text.strip()
        except AttributeError:
            pass
        if title:
            series_season, series_episode = self.util.extract_season_episode(title.replace(',', ''))
            for link in soup.select('.entry a'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link['href'],
                                         link_text=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )
