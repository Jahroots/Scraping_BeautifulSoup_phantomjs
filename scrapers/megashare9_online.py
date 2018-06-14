# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import requests


class MegaShare9Online(SimpleScraperBase):
    BASE_URL = 'http://megashare9.online'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'
        raise NotImplementedError('the website is offline')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Apologies, but no results were found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('a.clip-link'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
                image = result.select_one('img')['src']
            )

    def _parse_parse_page(self, soup):

        title = soup.select_one('h1.entry-title').text.strip()
        iframes = soup.select('iframe')
        for iframe in iframes:

            #call for sources
            if iframe['src'].find('http://putstream.com/') == 0:
                self.get_sources(iframe['src'], title)

            else:
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=iframe['src'],
                    link_title=title
                    )


    def get_sources(self, iframe_url, title):
        calls = ['a1', 'a2', 'a3']
        for call in calls:
            data = requests.get(iframe_url + '?source=' + call)

            if data.status_code == 200:
                soup = self.make_soup(data.text)
                iframes = soup.select('iframe')
                for iframe in iframes:
                    self.submit_parse_result(
                        index_page_title=self.util.get_page_title(soup),
                        link_url=iframe['src'],
                        link_title=title
                    )
            else:
                break
