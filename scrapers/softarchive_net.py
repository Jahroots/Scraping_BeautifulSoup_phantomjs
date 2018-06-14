# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SoftArchive(SimpleScraperBase):
    BASE_URL = 'https://sanet.st'
    OTHER_URLS = ['https://sanet.cd', 'https://my.sanet.cd', 'http://softarchive.la', 'http://my.sanet.me', 'http://sanet.me', 'http://softarchive.net']
    TRELLO_ID = 'yIUfdb5r'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):
        return super(SoftArchive, self).get(url, allowed_errors_codes=[403,], **kwargs)

    def _fetch_search_url(self, search_term, media_type, page=1):
        return self.BASE_URL + '/search/?q={}'.format(search_term)

    def _fetch_next_button(self, soup):
        # TODO pagination debug
        link = soup.select_one('.next_page a')
        self.log.debug('------------------------')
        return self.BASE_URL + '/search/' + link['href'] if link else None

    def _fetch_no_results_text(self):
        return u'No results found'

    def _parse_search_result_page(self, soup):
        for res in soup.select('a.cellMainLink'):
            self.submit_search_result(
                link_title=res.text.strip(),
                link_url=res.href
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.item_title').text
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.full_topic.clear a'):
            if link.attrs.get('target') == '_blank':
                self.submit_parse_result(index_page_title= self.util.get_page_title(soup),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )
