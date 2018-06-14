# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FileKnow(SimpleScraperBase):
    BASE_URL = 'http://fileknow.org'

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

    def search(self, search_term, media_type, **extra):
        soup = self.get_soup(self._fetch_search_url(search_term, media_type), allowed_errors_codes=[404])
        self._parse_search_results(soup)

    def _fetch_no_results_text(self):
        return u'Nothing Found'

    def _fetch_search_url(self, search_term, media_type, n=0):
        self.search_term = search_term
        self.media_type = media_type
        return self.BASE_URL + '/' + search_term + '?n=%d' % n

    def _parse_search_result_page(self, soup):
        for link in soup.select('.mediaVideo a') + soup.select('.content ul li h3 a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        self.log.debug('------------------------')
        return self._fetch_search_url(self.search_term,
                                      self.media_type,
                                      n=int(link['onclick'].split('navigate("n","')[1].split('"')[0])) \
            if link else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('.item-info h2').text
        series_season, series_episode = self.util.extract_season_episode(title)

        index_page_title = self.util.get_page_title(soup)

        for txt in soup.select('.item-info textarea'):
            for url in self.util.find_urls_in_text(str(txt)):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url,
                    link_title=title,
                    series_season=series_season,
                    series_episode=series_episode,
                    )
