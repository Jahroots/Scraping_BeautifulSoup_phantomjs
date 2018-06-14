# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TinyDDL(SimpleScraperBase):
    BASE_URL = 'http://www.rlslog.net'
    OTHER_URLS = [
        'http://www.rlslog.me',
        'http://rls-logs.com',
        'http://rlsslog.com',
        'http://nitrodl.com',
        'http://tinyddl.com']

    def setup(self):

        raise NotImplementedError('Duplicate of Rlslog scraper')

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, **kwargs)

    def _fetch_no_results_text(self):
        return 'Sorry, no posts matched your criteria'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next Page »')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for link in soup.select('.entrytitle a'):
            self.submit_search_result(
                link_title=link.text.strip(),
                link_url=link.href
            )

    def _parse_parse_page(self, soup):
        try:
            title = soup.select_one('.entrytitle').text.strip()
            series_season, series_episode = self.util.extract_season_episode(title)

            for link in soup.select('.entrybody a'):

                if 'Download' in link.parent.text and \
                        not link.text.startswith(self.BASE_URL) and \
                        link.href.startswith('http') and \
                                'cash-duck.com' not in link.href:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link.href,
                                             link_title=title,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )
        except:
            raise
