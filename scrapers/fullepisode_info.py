# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FullEpisode(SimpleScraperBase):
    BASE_URL = 'http://fullepisodeonline.net'
    OTHER_URLS = ['http://fullepisode.info', ]

    def setup(self):

        raise NotImplementedError('Now a spyware/credit card/ad site.  No content.')

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        # self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return 'No Results Found'

    def _parse_search_result_page(self, soup):
        for link in soup.select('a.post-info-title'):
            self.submit_search_result(
                link_title=link.text.strip(),
                link_url=link.href
            )

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('.post-title').text
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.post-wrapper table a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.href,
                                     link_title=link.text,
                                     series_season=season,
                                     series_episode=episode
                                     )
