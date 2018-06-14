# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class HdAreaOrg(SimpleScraperBase):
    BASE_URL = 'http://www.hd-area.org'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'deu'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s=search&q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'0 Artikel gefunden'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u' Vorwärts »')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for link in soup.select('div#content div.whitecontent a'):
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.download div.beschreibung a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
            )

