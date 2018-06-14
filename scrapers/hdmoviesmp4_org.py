# -*- coding: utf-8 -*-
import urlparse

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class HDmoviesmp4(SimpleScraperBase):
    BASE_URL = 'http://hdmoviesmp4.org'
    OTHER_URLS = ['http://MovieFry.Net']
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True
    # wapka.mobi sites group

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_search_url(self, search_term, media_type):

        return self.BASE_URL + '/search/index.xhtml?keyword=' + search_term

    def _fetch_no_results_text(self):
        return u'sorry the results you need not found'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='>')
        self.log.debug('---------------')
        return self.BASE_URL + next['href'] if next else None

    def _parse_search_result_page(self, soup):
        for link in soup.select('.media-heading a'):
            self.submit_search_result(link_url=link['href'],
                                      link_title=link.text
                                      )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.breadcrumb .active').text.strip().split(' - ')[0]

        for link in soup.select('.table.table-bordered a'):
            href = self.get_redirect_location(self.BASE_URL + link.href)

            if href:
                self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=href,
                                         link_title=title,
                                         # series_season=season,
                                         # series_episode=epis.text
                                         )
