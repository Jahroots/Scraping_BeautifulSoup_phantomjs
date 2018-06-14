# -*- coding: utf-8 -*-

import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase



class StreamTV2(SimpleScraperBase):
    BASE_URL = 'http://stream-tv4.me'
    OTHER_URLS = [
        'http://stream-tv3.co',
        'http://stream-tv3.me',
        'http://stream-tv2.ag',
        'http://streamtvlinks.me',
        'http://stream-tv-series.net',
        'http://stream-tv2.to'
    ]

    def setup(self):
        raise NotImplementedError('Duplicate of stream_tv_series_info.py')
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

    def get(self, url, **kwargs):

        return super(StreamTV2, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def _fetch_no_results_text(self):
        return 'Not Found'

    def _fetch_no_results_pattern(self):
        return 'Not\s*Found'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='»')
        self.log.debug('------------------------')
        return next['href'] if next else None

    def _parse_search_result_page(self, soup):

        for link in soup.select('.entry ul li a'):
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text)

    def _parse_parse_page(self, soup):
        try:
            index_page_title = self.util.get_page_title(soup)
            entry_title = soup.select_one('.entry-title')
            title = ''
            if entry_title:
                title = entry_title.text
            series_season, series_episode = self.util.extract_season_episode(title)
            for iframe in soup.find_all('div', id=re.compile('postTabs_\d+')):
                iframe_source = iframe.find('iframe')
                src = iframe_source.get('src', iframe_source.get('data-src', None))
                if src:
                    self.submit_parse_result(index_page_title=index_page_title,
                                             link_text=title,
                                             link_url=src,
                                             series_season=series_season,
                                             series_episode=series_episode,)
        except:
            pass
