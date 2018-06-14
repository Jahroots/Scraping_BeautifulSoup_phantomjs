# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class BaixeTurbo(SimpleScraperBase):
    BASE_URL = 'http://www.sobaixar.net'
    LONG_SEARCH_RESULT_KEYWORD = 'android'
    OTHERS_URLS= ['https://www.sobaixar.net']
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    SINGLE_RESULTS_PAGE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        #self.register_scraper_type(ScraperBase.SCRAPER_TYPE_P2P)
        self.search_term_language = "por"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH,
                          self.BASE_URL)

        self.register_url(ScraperBase.URL_TYPE_LISTING,
                          self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Resultados não encontrados.'

    def _fetch_no_results_pattern(self):
        return 'o\s*encontrad[oa]'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'Próxima »')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('.name-article-mini a'):
            if 'download' not in result.href:
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result['title']
                )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        # Links are behind a tracker, but a really simple one:
        # http://www.loadbr.info/link/?url=http://bitshare.com/files/9zlqj661/GUARDBDDUAL.zip.html
        index_title = self.util.get_page_title(soup)
        urls = set()
        for link in soup.select('div.entry a') + soup.select('.entry.clearfix p a'):
            url = link.get('href')
            if not url:
                continue
            if url.startswith('http://www.loadbr.info/link/?url='):
                parsed_url = url[33:]
                if parsed_url.startswith('http'): # or parsed_url.startswith('magnet'):
                    urls.add(url[33:].strip())
                else:
                    self.log.debug('Found non http link: %s', link['href'])
            #elif 'sobaixar.com' not in url:
            #    self.submit_parse_result(index_page_title=soup.title.text.strip(),
            #                             link_url=url.strip()
            #                             )
        if len(urls)>0:
            for url in urls:
                self.submit_parse_result(index_page_title=index_title,
                                     link_url=url
                                     )
