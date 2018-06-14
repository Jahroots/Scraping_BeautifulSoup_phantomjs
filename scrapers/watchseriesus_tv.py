# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class WatchSeriesUS(SimpleScraperBase):
    BASE_URL = 'http://tvseries4u.com'
    OTHERS_URLS = ['asdl_us', 'http://watchseriesus.tv']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        # self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Apologies, but no results were found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.movief a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.filmcontent > h1').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.autohyperlink'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )
