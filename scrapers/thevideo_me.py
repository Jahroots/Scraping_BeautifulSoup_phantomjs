# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, VideoCaptureMixin
import json
import re


class TheVideoMe(SimpleScraperBase, VideoCaptureMixin):
    BASE_URL = 'https://thevideo.me'
    OTHER_URLS = ['http://thevideo.me', ]
    LONG_SEARCH_RESULT_KEYWORD = '2017'
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP , ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]
    SINGLE_RESULTS_PAGE = True

    def _fetch_search_url(self, search_term, media_type, page=1):
        return self.BASE_URL + u'/ajax/search?page={}&search_query={}'.format(page,
            self.util.quote(search_term.decode('utf8')))

    def search(self, search_term, media_type, **extra):
        soup = json.loads(self.get_soup(self._fetch_search_url(search_term, media_type)).text)
        results_text = soup['response']['results']
        if not results_text:
            return self.submit_search_no_results()
        for page in range(1, 100):
            soup = json.loads(self.get_soup(self._fetch_search_url(search_term, media_type, page=page)).text)
            results_text = soup['response']['results']
            for result_text in results_text:
                if 'DELETED' in result_text['file_status']:
                    continue
                link =self.BASE_URL+'/embed-'+result_text['download_link'].split('/')[-1]+'.html'
                self.submit_search_result(
                            link_title=result_text['file_title'],
                            link_url=link,
                            image = result_text['img_default']
                        )
            if not results_text:
                break

    def _parse_parse_page(self, soup):
        sources = soup.find(text=re.compile(u'sources:')).split('sources:')[-1].split(']')[0]+']'
        files_url = json.loads(sources)[0]['file']
        key = soup.find(text=re.compile('lets_play_a_game=')).split('lets_play_a_game=')[-1].split(';')[0].strip("'")
        data_url = self.BASE_URL+'/vsign/player/'+key
        data_id = self.get(data_url).content
        found = re.search('jwConfig', data_id).group().strip("|")
        source_url = files_url+'?direct=false&ua=1&vt='+found
        if source_url:
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=source_url)
