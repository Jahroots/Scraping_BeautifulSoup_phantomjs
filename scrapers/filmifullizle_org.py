# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import VKAPIMixin


class FilmiFullizleOrg(SimpleScraperBase, VKAPIMixin):
    BASE_URL = 'http://www.filmifullizle.org'
    OTHERS_URLS = ['https://www.filmifullizle.org']
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "tur"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL,]:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Üzgünüz. Aradığınız kriterlere uygun sonuç bulunamadı'

    def search(self, search_term, media_type, **extra):
        soup = self.get_soup(self.BASE_URL + '/token.php')
        token = soup.select_one('input[name="token"]')['value']
        soup = self.get_soup(self.BASE_URL +  '/i.php?s={}&token={}'.format(search_term, token))
        self._parse_search_result_page(soup)

    def _fetch_next_button(self, soup):
        link = soup.select_one('a[class="next page-numbers"]')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):

        if unicode(soup).find(self._fetch_no_results_text()) > 0:
            return self.submit_search_no_results()

        results = soup.select('a.item-title')
        for result in results:
            # Submit the main url.
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title'],
                image=self.util.find_image_src_or_none(result, 'img')
            )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)

    def _parse_parse_page(self, soup):
        title_block = soup.select_one('.post h2')
        title = title_block and title_block.text or ''
        base = soup._url
        for i in range (2, 7):
            soup = self.get_soup( base + '/' + str(i))
            for result in soup.select('div.source p iframe'):
                url = result['src']
                if url.find('http') == -1:
                    url = 'http:' + url
                self.submit_parse_result(
                    index_page_title= self.util.get_page_title(soup),
                    link_url= url,
                    link_title=title,
                )