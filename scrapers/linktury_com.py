# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Linktury(SimpleScraperBase):
    BASE_URL = 'http://www.linktury.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        self.media_type = media_type
        return self.BASE_URL + '/download-search.php?q={}&log=1&x=0&y=0'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return 'has returned'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next Page »')
        self.log.debug('------------------------')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.i2 a' if self.media_type in (self.MEDIA_TYPE_FILM, self.MEDIA_TYPE_TV)
                                  else '.i5 a'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.top-l > strong').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.dl-links a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.text,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )
