# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SCRAPERNAME(SimpleScraperBase):
    BASE_URL = 'http://XXX'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'XXX'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = (soup.find('a', itemprop='name') or soup.select_one('.blogs h2')).text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.blogs a'):
            self.submit_parse_result(
                index_page_title=soup.title.text.strip(),
                link_url=link['href'],
                link_title=title,
                series_season=season,
                series_episode=episode
            )
