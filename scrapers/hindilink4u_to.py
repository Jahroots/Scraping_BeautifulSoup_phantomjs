#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class HindiLinks4UTo(SimpleScraperBase):

    BASE_URL = 'https://www.hindilinks4u.to'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Apologies, but no results were found.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'nextpostslink')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.post'):
            img = result.select('span.clip img')[0]
            link = result.select('h2.entry-title a')[0]
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=img['src']
            )

    def _parse_parse_page(self, soup):
        # Embed links at the top of the page are embedded using jquery.
        # Suck out any
        # data-href=\\"....\\"
        for datahref in re.findall('data-href=\\\\"(.*?)\\\\"', str(soup)):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=datahref,
                                     )
        # And any links within the content.
        for link in soup.select('div.entry-content a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     link_title=link.text
                                     )

