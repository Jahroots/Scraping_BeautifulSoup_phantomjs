# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin
import json

class Video2kIs(SimpleScraperBase):
    BASE_URL = 'http://www.cmovieshd.is'
    OTHER_URLS = ['http://www.video2k.is']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    SINGLE_RESULTS_PAGE = True

    def _fetch_search_url(self, search_term, media_type):
        return '{}/?c=movie&m=quickSearch&key=4164OPTZ98adf546874s4&keyword={}'.format(self.BASE_URL, search_term)

    def _fetch_no_results_text(self):
        return 'Apologies, but no movies were found'

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        response = json.loads(self.get(self._fetch_search_url(search_term, media_type), headers = {'X-Requested-With' : 'XMLHttpRequest'}).text)
        if not response or len(response) == 0:
            return self.submit_search_no_results()
        for item in response:
            url = self.BASE_URL + '/' + item['title'].lower().replace(':', '').replace("'", '').replace(' ', '-') +   '-stream-' + item['id'] + '.html'
            self.submit_search_result(
                    link_url=url,
                    link_title= item['title'],
                    image= item['img_link'],
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('#player iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=link.text,
            )
