# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class DDLSpotCom(SimpleScraperBase):
    BASE_URL = 'http://www.ddlspot.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'has found 0 results on DDLSpot'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?m=1&q=' + search_term

    def _fetch_next_button(self, soup):
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        soup = self.get_soup(soup._url, headers=headers)
        link = soup.find('a', text='Next Page »')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = False
        headers={'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        soup = self.get_soup(soup._url, headers=headers)
        for result in soup.select('table.download tr td.c a'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text,
            )
            found = True
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
        soup = self.get_soup(soup._url, headers=headers)
        for links_box in soup.select('div.links-box'):
            for link in links_box.contents:
                if unicode(link).strip().startswith('http'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link.strip()
                                             )
