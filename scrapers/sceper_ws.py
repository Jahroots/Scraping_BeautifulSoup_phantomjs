# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, DuckDuckGo


class Sceper_ws(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://sceper.ws'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self._request_connect_timeout = 300
        self._request_response_timeout = 600

        raise NotImplementedError('Domain is for sale.')

    USER_AGENT_MOBILE = False

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[524,], **kwargs)

    def _fetch_no_results_text(self):
        return 'Try refining your search'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        return link['href'] if link else None


    def _parse_parse_page(self, soup):

        title = soup.select_one('h1.title')
        season = None
        episode = None
        if title:
            title = title.text.strip()
            season, episode = self.util.extract_season_episode(title)

        entrybody = soup.select_one('.entry-content')
        for p in entrybody.findAll('p'):
            if 'DOWNLOAD' in p.text.upper():
                for link in p.findAll('p'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link.parent.a['href'],
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )

        # links in comments
        for link in soup.select('.comment-content a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )
