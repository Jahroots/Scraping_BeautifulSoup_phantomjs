# coding=utf-8
import base64
import urllib2
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class DescargatelocorpCom(SimpleScraperBase):
    BASE_URL = 'https://www.descargatelocorp.com'
    OTHER_URL = ['http://www.descargatelocorp.com']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}&submit=Buscar'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'По запросу ничего не найдено'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        any_results = False
        for results in soup.select('a.post-thumbnail'):
            result = results['href']
            title = results['title']
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.titulo-post h2').text.strip()
        for result in soup.select('div.boxdescargas a'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=result.href,
                link_text=title,
            )


