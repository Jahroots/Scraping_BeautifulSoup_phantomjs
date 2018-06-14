# -*- coding: utf-8 -*-
import base64

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Repian(SimpleScraperBase):
    BASE_URL = 'https://list.repian110.com'
    OTHER_URLS = [ 'http://www.repian.com', 'http://list.repian.com', 'http://www.list.repian110.com',
                   'http://www.repian110.com']
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'chi'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[502], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?keyword=' + search_term

    def _fetch_no_results_text(self):
        return u'抱歉，没有找到“'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='下一页')
        self.log.debug('------------------------')
        return self.BASE_URL + link['href'] if link else None

    def search(self, search_term, media_type, **extra):
        soup = self.make_soup(self.get(self._fetch_search_url(search_term, media_type)).text)
        self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        results = soup.select('ul.show-list li a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()
        
        for link in results:
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text)

    @staticmethod
    def _de_thunder(thunurl):
        return base64.b64decode(thunurl[10:].encode()).decode('gbk')[2:-2]

    def _parse_qqdl(self, url):
        return base64.b64decode(url[7:].encode()).decode('gbk')

    def parse(self, parse_url, **extra):
        try:
            soup = self.make_soup(self.get(parse_url).content.decode('gb2312', 'ignore'))  #, from_encoding='gb2312')
            self._parse_parse_page(soup)
        except Exception as e:
            self.log.warning(str(e))

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2').text.strip()
        series_season, series_episode = self.util.extract_season_episode(title)

        for thund in soup.select('.thunderhref'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=self._de_thunder(thund['value']),
                                     link_text=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )

        for qqdl in soup.select('.qqdl'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=self._parse_qqdl(qqdl['qhref']),
                                     link_text=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )
