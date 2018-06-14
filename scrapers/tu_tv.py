# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from bs4 import Comment
import re
import json


class TuTv(SimpleScraperBase):
    BASE_URL = 'http://tu.tv'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    USER_AGENT_MOBILE = False
    WEBDRIVER_TYPE= 'phantomjs'
    REQUIRES_WEBDRIVER = ('parse',)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/buscar/?str={}&todas=1'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No se han encontrado videos con la búsqueda'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Siguiente ')
        return self.BASE_URL+next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for results in soup.select('div.datos_video h2 a'):
            if not results:
               return self.submit_search_no_results()
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )


    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        scripts = soup.find('script', text= re.compile(r'codVideo'))
        code = None
        for script in scripts:
            code = script.split('codVideo=')[1].split(';')[0]

        if code:
            response = self.get('http://tu.tv/tutvplayer/videoUrl.php?codVideo={}'.format(code)).text
            src=json.loads(response)[0]['src']

            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url= src,
            )