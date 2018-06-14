# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class DizilerCom(SimpleScraperBase):
    BASE_URL = 'https://www.diziler.com'
    OTHER_URLS = ['http://www.diziler.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    USERNAME = 'Faing1942'
    PASSWORD = 'ahtaeZ6sh'
    EMAIL = 'mariormeads@teleworm.us'
    USER_AGENT_MOBILE = False
    LONG_SEARCH_RESULT_KEYWORD = '2016'

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/arama-sonuc?keyword={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Aradığınız kritere uygun sonuç bulunamamıştır'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_results(self, soup):
        if not soup.select('div#widget_icerik_liste_4lu_dikey_140_200_6 a.series2-item'):
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        for result in soup.select('div#widget_icerik_liste_4lu_dikey_140_200_6 a.series2-item'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        #self.log.debug(soup.select_one('div.tooplay_video'))
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        link = soup.select_one('div.tooplay_video')
        if link:
            movie_link = re.search("""tp_file:'(.*?)'""",  link['data-tp']).groups(0)[0]
            movie_title = re.search("""tp_title:'(.*?)'""", link['data-tp']).groups(0)[0]
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_title=movie_title,
                series_season=series_season,
                series_episode=series_episode,
            )
