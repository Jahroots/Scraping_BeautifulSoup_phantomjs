# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import re
import urllib

class TupeliculaTv(SimpleScraperBase):
    BASE_URL = 'http://www.tupelicula.tv'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search?q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'No data.'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('#movie-list a'):
            link = result
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text
            )


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h2.tit').text
        referer = soup.select_one('#playerframe')['data-src']
        self.log.debug(referer)
        sources = self.get_soup(referer).select('a[data-id]')
        get_url = 'http://www.tupelicula.tv/player/rep/'
        for a in sources:
            id = a['data-id']
            soup = self.get_soup(
                get_url + id,
                headers ={'Referer': referer}
            )
            scripts = soup.select('script')
            for script in scripts:
                for url in re.findall('src=\\\\"(.*?)"', script.text):
                    url = url.replace('\\', '')
                    if url.startswith('//'):
                        url = 'http:{}'.format(url)
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=url,
                        link_title=title
                    )
