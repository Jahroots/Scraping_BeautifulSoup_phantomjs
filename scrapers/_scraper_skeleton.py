# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase


class SCRAPERNAME(ScraperBase):
    BASE_URL = 'XXX'  # Fudge: Do not change this value (here), it's used by the framework to know this is a base class

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '%s' % self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        if unicode(soup).find(u'SOMETHINGSOMETHING') >= 0:
            return self.submit_search_no_results()

        for result in soup.select('XXXX'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result['title']
            )

        next_button = soup.select('XXX')
        if next_button and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    self.BASE_URL + next_button[0]['href'])
            )

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        for result in soup.select('XXXX'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=result['href'],
                                     link_title=result.text
                                     )
