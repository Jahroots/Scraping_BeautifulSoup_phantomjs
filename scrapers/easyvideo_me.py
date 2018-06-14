# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class EasyVideoMe(SimpleScraperBase):
    BASE_URL = 'http://www.easyvideo.me'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Not Found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.postlist a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.premiumdll h1').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('p iframe'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link['src'],
                link_title=title,
                series_season=season,
                series_episode=episode
            )
