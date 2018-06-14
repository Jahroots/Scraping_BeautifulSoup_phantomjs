# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmeOnline2016(SimpleScraperBase):
    BASE_URL = 'http://www.filmeonline.ws'
    OTHERS_URLS = ['http://www.filmeonline2016.ro/']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rom'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Sorry, but nothing matched your search criteria'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next ›')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('li[class="border-radius-5 box-shadow"] a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1[itemprop="name"]').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('iframe'):
            #self.log.debug(link)
            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url=link['src'],
                link_title=title,
                series_season=season,
                series_episode=episode
            )
