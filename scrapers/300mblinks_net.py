# -*- coding: utf-8 -*-
import base64

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class ThreeHunredMBlinks(SimpleScraperBase):
    BASE_URL = 'http://300mbhdmovies.com'
    OTHER_URLS = ['http://300mblinks.net', ]
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        raise NotImplementedError('Website not available')

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return u'Nothing found for this search term'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='»')
        self.log.debug('---------------')
        return next['href'] if next else None

    def _parse_search_result_page(self, soup):
        for link in soup.select('.title.entry-title a'):
            self.submit_search_result(link_url=link.href,
                                      link_title=link.text
                                      )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.post-title').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.sentry div pre a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=base64.decodestring(link.href[43:])
                                     if link.href.startswith('http://spaste.com')
                                     else link.href,
                                     link_title=title,
                                     series_season=series_season,
                                     series_episode=series_episode
                                     )
