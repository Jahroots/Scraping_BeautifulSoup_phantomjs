# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import json


class Filmesonlinehd11Cc(SimpleScraperBase):
    BASE_URL = 'http://www.filmesonlinehd7.cc'
    OTHERS_URLS = ['http://www.filmesonlinehd11.cc', 'http://chishare.cc/', 'http://www.compartilhabrasil.org']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "por"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in self.OTHERS_URLS + [self.BASE_URL]:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return u'Conteúdo não disponível'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search?q={}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        link = soup.select_one('i[class="angle right icon"]')
        if link and link.parent:
            return 'http:' + link.parent['href']
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class="ui six special doubling cards"] a[class="ui card"]')
        if not results and len(results) == 0:
               return  self.submit_search_no_results()

        for result in results:
            a = result.href
            if a.find('http:') == -1:
                a = 'http:' + a

            soup = self.get_soup(a)
            link = soup.select_one('div[class="ui embed dimmable"]')
            if link:
                self.submit_search_result(
                    link_url=link['data-url'],
                    link_title=result.text,
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.find('h1')

        scripts = soup.select('script')
        for script in scripts:
            if 'var links' in script.text:
                links = script.text.split('var links=')[1].split(';')[0]
                links = json.loads(links)
                self.log.debug(links)
                for url in links:
                    if url['Url'] and len(url['Url']) > 0:
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=url['Url'],
                            link_title=url['Nome'],
                        )
                break
        return


