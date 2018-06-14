# coding=utf-8

import re
import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.exceptions import ScraperException


class RepelisTv(SimpleScraperBase):
    BASE_URL = 'https://repelis.tv'
    OTHER_URLS = ['http://www.repelis.tv']

    LONG_SEARCH_RESULT_KEYWORD = 'man'

    def setup(self):
        raise NotImplementedError('duplicate scraper for https://repelis.tv url')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def get(self, url, **kwargs):
        return super(RepelisTv, self).get(url, allowed_errors_codes=[403], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/buscar/?s=' + self.util.quote(search_term)

    def soup_each(self, urls):
        for url in urls:
            try:
                soup = self.get_soup(url)
            except ScraperException as error:
                self.log.error("Scraper Error: %s", error)
                continue
            yield soup

    def search(self, search_term, media_type, **extra):
        for soup in self.soup_each([self._fetch_search_url(search_term, media_type)]):
            self._parse_search_results(soup)

    def _fetch_no_results_text(self):
        return u'No se han encontrado resultados para tu búsqueda'

    def _fetch_next_button(self, soup):
        # No next link - find the 'current', then if there is a class='single-page' after that.
        current = soup.select('div.pagenavi span.current')
        if not current:
            return None
        next_page = current[0].next_sibling
        if next_page and \
                        'class' in next_page.attrs and \
                        'single_page' in next_page.attrs['class']:
            self.log.debug('--------------------')
            time.sleep(.25)
            return next_page['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('ul.search-results-content li'):
            image = None
            img = result.find('img')
            if img:
                image = img['src']
            link = result.select_one('div.col-xs-10 a')
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text.strip(),
                image=image,
            )

    def __handle_link(self, url, soup):
        # XXX helper?
        if url.startswith('http://www1.repelis.tv'):
            soup = self.get_soup(url)
            self._parse_iframes(soup)
            # Check for proxy.link=XXXX
            srch = re.search('proxy\.link=([^\"]*)', str(soup))
            if srch:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=srch.group(1))
        elif 'adserver' not in url:
            if url.startswith(self.BASE_URL):
                sup = self.get_soup(url)
                link_url = sup.select_one('iframe')
                if link_url:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link_url.get('src'))
                # else:
                #     self.submit_parse_result(index_page_title=soup.title.text.strip(),
                #                              link_url=url)

    def _parse_parse_page(self, soup):
        # for iframe in soup.select('div.tab-content iframe'):
        #     self.__handle_link(iframe.get('src', iframe.get('data-src', None)), soup)

        for link in soup.select('.btn.btn-xs.btn-info'):
            self.__handle_link(link['href'], soup)
