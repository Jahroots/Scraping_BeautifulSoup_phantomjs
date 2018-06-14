# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class NewpctCom(SimpleScraperBase):
    BASE_URL = 'http://www.newpct.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ScraperBase.SCRAPER_TYPE_P2P, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    def _fetch_no_results_text(self):
        return u'No hemos encontrado resultados'

    def search(self, search_term, media_type, **extra):
        self._parse_search_result_page(
            self.post_soup(
                self.BASE_URL + '/buscar-descargas/',
                data = {
                    'q': search_term,
                }
            )
        )

    def _parse_search_result_page(self, soup):
        if 'No hemos encontrado' in unicode(soup):
            return self.submit_search_no_results()


        for result in soup.select('table#categoryTable tr'):
            link = result.select_one('a')
            if not link:
                continue
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link_block in soup.select('table#tabsTable a'):
            url = link_block.get('href')
            if url and \
                url.startswith('http'):
                if not url.startswith(self.BASE_URL):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=url,
                    )
            else:
                on_click = link_block.get('onclick', '')
                for link in self.util.find_urls_in_text(on_click):
                    if not link.startswith(self.BASE_URL):
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=link,
                        )
