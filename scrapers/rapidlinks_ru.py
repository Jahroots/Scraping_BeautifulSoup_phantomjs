# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class RapidLinks(SimpleScraperBase):
    BASE_URL = 'http://rapidlinks.org'
    OTHER_URLS = ['http://rapidlinks.ru']

    LONG_SEARCH_RESULT_KEYWORD = 'mother'
    SINGLE_RESULTS_PAGE = True


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term, media_type, page=1):
        return self.BASE_URL + u'/search/?q={}&w=desc{}'.format(
            self.util.quote(search_term.decode('utf8').encode('cp1251', 'replace')),
            '&p=%d' % page if page > 1 else '')

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        for link in soup.select('.tbl_line1 a'):
            if '/?lnk' in link.href:
                self.submit_search_result(
                    link_title=link.text.strip(),
                    link_url=self.BASE_URL + link.href
                )

    def _fetch_no_results_text(self):
        return u'Ничего не найдено!'

    def _parse_parse_page(self, soup):
        title = soup.select_one('.tbl_head h1').text
        season, episode = self.util.extract_season_episode(title)

        for link in soup.find_all('a', target="_blank"):
            if link.href.startswith('http'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href.replace('dl.rapidlinks.org', 'turbobit.net'),
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )
