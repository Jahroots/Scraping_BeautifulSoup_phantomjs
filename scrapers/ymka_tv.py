# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class YmkaTv(SimpleScraperBase):
    BASE_URL = 'http://ymka.co'
    OTHER_URLS = ['http://www.ymka.tv', 'http://ymka.tv']
    LONG_SEARCH_RESULT_KEYWORD = 'Голос'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?do=search'

    def _fetch_no_results_text(self):
        return None

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self._fetch_search_url(search_term, media_type), data = { 'do' : 'search',
                                                                                        'subaction' : 'search',
                                                                                         'search_start' : 0,
                                                                                         'full_search ' : 0,
                                                                                          'result_from' : 1,
                                                                                          'story' : search_term}
                              )
        self._parse_search_result_page(soup)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return 'http:'+link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.short_story div.title-short a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1[itemprop="name"]').text.strip()
        season, episode = self.util.extract_season_episode(title)

        index_page_title = self.util.get_page_title(soup)

        for src in soup.select('div[class*="box"] iframe'):
            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url='http:' + src['src'] if src['src'].startswith('//') else src['src'],
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )


