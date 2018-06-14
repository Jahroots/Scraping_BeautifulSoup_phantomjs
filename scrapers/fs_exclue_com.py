# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FsExclueCom(SimpleScraperBase):
    BASE_URL = 'http://www.fs-exclue.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "fra"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Pas de réponse'

    def _fetch_next_button(self, soup):
        curr_page_link = soup.select_one('.wp-pagenavi .current')
        if curr_page_link and curr_page_link.next_sibling.name == 'a':
            self.log.debug('----------------')
            return curr_page_link.next_sibling['href']

    def _parse_search_result_page(self, soup):
        found = False

        for result in soup.select('div.post div.title h2 a'):
            found = True
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        # All of the links are 'hidden' using protege-ddl.com; use that as
        # our search.
        for link in soup.findAll('a', href=re.compile('^http://protege-ddl.com')):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.get('href'),
                                     link_title=link.text
                                     )
