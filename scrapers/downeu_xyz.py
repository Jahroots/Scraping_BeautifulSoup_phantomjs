# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class Downeu(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.downeu.xyz'
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 20
        self.media_type_to_category = 'film 15, tv 13'
        self.showposts=0

    def get(self, url, **kwargs):
        return super(Downeu, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))

    def _parse_search_result_page(self, soup):
        for result in soup.select('.fullLink a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.title h2')
        if title:
            title = title.text
        else:
            title = soup.select_one('h1.title').text

        season, episode = self.util.extract_season_episode(title)

        for box in soup.select('div.quote div a[target="_blank"]'):

            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=box.href,
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode,
                                             )
