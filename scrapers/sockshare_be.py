# -*- coding: utf-8 -*-
from time import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CacheableParseResultsMixin


class Sockshare(CacheableParseResultsMixin, SimpleScraperBase):
    BASE_URL = 'https://me123movies.com'
    OTHER_URLS = [
        'https://movietv4u.pro',
        'http://www.watchfree.cx'
        'http://www.putlocker.fi',
        'http://www.putlocker121.com',
        'http://www.putlockerstreaming.com',
        'http://www.sockshare.be',
        'http://wewatchmoviesfree.eu',
        'http://www.putlocker1.co',
    ]
    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = '8hIu9CD9'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self._request_size_limit = (2048 * 2048 * 50)  # Bytes
        self._ignore_chunked_encoding_error = True

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def get_soup(self, url, **kwargs):
        return super(Sockshare, self).get_soup(url, allowed_errors_codes=[404], **kwargs)



    def search(self, search_term, media_type, **extra):
         soup = self.post(self.BASE_URL + '/ajax/search.php',
                          data={'q': search_term, 'limit' : 1000, 'timestamp' : int(time()), 'verifiedCheck':''}).json()

         self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        found = 0

        for l in soup:

            found = 1
            link = l['permalink']
            title = l['title']

            self.submit_search_result(
                link_title=title,
                link_url=link
            )
        if not found:
            self.submit_search_no_results()

    def _parse_search_result_pagex(self, soup):
        found = 0

        links = [{'link_url': link.find('a')['href'], 'link_title': link.find('a').text.strip()} for ul in
                 soup.find_all('ul', 'span-24') if ul for link in ul.find_all('h5') if link and link.find('a')]
        for l in links:
            found = True
            self.submit_search_result(
                link_title=l['link_title'],
                link_url=l['link_url']
            )
        if not found:
            self.submit_search_no_results()

    def _fetch_no_results_text(self):
        return 'We are sorry'

    def _fetch_next_button(self, soup):
        return

    def _parse_parse_page(self, soup):
        title = ''
        try:
            title = soup.select_one('div.mvic-desc h3').text
        except AttributeError:
            pass
        if title:
            series_season, series_episode = self.util.extract_season_episode(title)
        links = {}
        for link in soup.select('.current a'):
            if link.href.startswith('/'):
                continue
            links[link.href] = {'index_page_title': soup.title.text.strip(),
                                'link_url': link.href.strip(),
                                'link_title': title,
                                'series_season': series_season,
                                'series_episode': series_episode}

        for link in links:
            self.submit_parse_result(index_page_title=links[link]['index_page_title'],
                                     link_url=links[link]['link_url'].strip(),
                                     link_title=links[link]['link_title'],
                                     series_season=links[link]['series_season'],
                                     series_episode=links[link]['series_episode'],
                                     )
        for link in soup.select('ul.filter a'):
            if link.href.startswith('/'):
                continue
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=link.href.strip(),
                                     link_title=link.text,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )
