# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Media4shared(SimpleScraperBase):
    BASE_URL = 'http://www.media4play.li'
    OTHER_URLS = ['http://media4shared.com']

    LONG_SEARCH_RESULT_KEYWORD = 'rock'
    SINGLE_RESULTS_PAGE = True

    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?do=search&subaction=search&story=' + search_term

    def _parse_search_result_page(self, soup):
        if 'Search results for ' in str(soup):

            for link in soup.select('.eTitle a')[1:]:
                self.submit_search_result(
                    link_title=link.text,
                    link_url=link.href
                )
        else:
            self.submit_search_no_results()

    def _fetch_no_results_text(self):
        return 'No results found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('.eTitle').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for code_box in soup.select('.quote'):
            text = str(code_box).replace('<br/>', ' ')
            for url in self.util.find_urls_in_text(text):
                if url.startswith('http'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=url,
                                             link_title=title,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )


