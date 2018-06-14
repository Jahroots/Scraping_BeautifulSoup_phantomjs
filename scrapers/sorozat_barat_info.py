# -*- coding: utf-8 -*-
import json

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SorozatBarat(SimpleScraperBase):
    BASE_URL = 'https://www.sorozat-barat.club'
    OTHER_URLS = [
        'http://www.sorozat-barat.club'
        'http://sorozatbarat.org',
        'http://www.sorozat-barat.info'
    ]
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Website requires invitation to register and view results.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'hun'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        # self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):
        found = False
        for result in json.loads(self.get(self.BASE_URL + '/series/autocompleteV2?term=' + search_term).text):
            self.submit_search_result(
                link_url=self.BASE_URL + result['url'],
                link_title=result['label']
            )
            found = True
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('.navTitle').text

        for btn in soup.select('.links button'):
            soup2 = self.get_soup(btn.parent.href)
            for link in soup2.select('#hosts a img'):
                soup3 = self.get_soup('http://www.filmorias.com' + link.parent.href)
                url = soup3.select_one('#searchform a').href
                url = 'http'+url.split('/http')[1] if url.startswith('http://adf.ly/') else url

                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         # series_season=season,
                                         # series_episode=episode
                                         )
