# -*- coding: utf-8 -*-

import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Funmasti(SimpleScraperBase):
    BASE_URL = 'http://www.mastiya.com'
    OTHER_URLS = ['http://funmasti.org']

    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        # self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        raise NotImplementedError

    def _get_search_results(self, search_term, media_type, page=1, search_url=None):
        if search_url is not None:
            return self.get_soup(search_url)

        data = dict(s='', securitytoken='guest', do='process', searchthreadid='', query=search_term, titleonly=1,
                    searchuser='', starteronly=0, exactname=1, replyless=0, replylimit=0, searchdate=0,
                    beforeafter='after', sortby='lastpost', order='descending', showposts=0, childforums=1,
                    dosearch='Search Now')
        data.update(
            {'forumchoice[]': 70 if media_type == self.MEDIA_TYPE_FILM else 0})

        try:

            for _ in xrange(10):
                soup = self.post_soup(self.BASE_URL + '/search.php?do=process', data=data, allowed_errors_codes=[404])

                if 'Sorry, but you can only perform one search every 10 seconds' in str(soup):
                    self.log.debug('sleeping...')
                    time.sleep(int(str(soup).split('Please wait another ')[1].split(' second')[0]) + .33)
                else:
                    return soup

        except Exception as e:
            self.log.exception(e)
            # self.show_in_browser(soup)
            raise e

    def search(self, search_term, media_type, **extra):
        self.search_term = search_term
        self.media_type = media_type

        page = 1

        search_url = None
        while True:
            soup = self._get_search_results(search_term, media_type, page=page, search_url=search_url)
            # self.show_in_browser(soup)

            no_results_text = self._fetch_no_results_text()
            if no_results_text and unicode(soup).find(no_results_text) >= 0:
                return self.submit_search_no_results()

            # self.show_in_browser(soup)
            self._parse_search_result_page(soup)
            search_url = self._fetch_next_button(soup)
            if search_url is None:
                break
            page += 1

    def _parse_search_result_page(self, soup):

        for link in [a for a in soup.select('a') if a.attrs.get('id', '').startswith('thread_title')]:
            self.submit_search_result(
                link_title=link.text,
                link_url=self.BASE_URL + '/' + link.href
            )

    def _fetch_no_results_text(self):
        return 'Sorry - no matches. Please try some different terms'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>')
        self.log.debug('------------------------')
        return self.BASE_URL + '/' + link['href'] if link else None

    def _parse_parse_page(self, soup):
        title = soup.title.text
        series_season, series_episode = self.util.extract_season_episode(title)

        # for link in soup.select('.alt2'):
        #     if not link.href.startswith(self.BASE_URL) and link.href.startswith('http'):
        #         self.submit_parse_result(
        #             link_url=link.href,
        #             link_title=title,
        #             series_season=series_season,
        #             series_episode=series_episode,
        #         )

        for box in soup.select('.alt2'):
            for url in self.util.find_urls_in_text(box.text):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )
