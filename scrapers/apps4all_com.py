# -*- coding: utf-8 -*-

import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Apps4all(SimpleScraperBase):
    BASE_URL = 'http://www.apps4all.com'
    OTHER_URLS = ['http://filelinkz.com']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        kwargs['headers'] = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
        return super(self.__class__, self).get(url, **kwargs)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/app-search.php?q={}&log=1&x=0&y=0'.format(search_term)

    def _fetch_no_results_text(self):
        return 'Nothing Found'

    def _fetch_next_button(self, soup):
        next = soup.select_one('div.pages')
        if next:
            next = next.find('a', text=re.compile("Next"))
            if not next:
                return None
        else:
            return None
        self.log.debug('------------------------')

        return self.BASE_URL + next['href']


    def _parse_search_result_page(self, soup):
        found = 0
        for link in soup.select('.dl-name strong a'):
            found = 1
            self.submit_search_result(
                link_url=self.BASE_URL + link['href'],
                link_title=link.text)

        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.title.text.split('|')[0].strip()
        series_season, series_episode = self.util.extract_season_episode(title)

        for dl in soup.select('.quote a'):
            if dl['href'].split('/') > 2:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=dl['href'],
                                         link_text=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

        for box in soup.select('.quote'):
            for url in self.util.find_urls_in_text(box.text):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )