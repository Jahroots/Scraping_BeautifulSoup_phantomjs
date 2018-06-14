#coding=utf-8

import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import OpenSearchMixin, SimpleScraperBase

class MeijuttCom(SimpleScraperBase):

    BASE_URL = 'http://www.meijutt.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'chi'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
       return self.BASE_URL + \
               '/search.asp?page=1&searchword={}&searchtype=-1'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        next = soup.find('a', text=u'下一页')
        return self.BASE_URL + '/search.asp'+next['href'] if next else None

    def _fetch_no_results_text(self):
        return  u'找到 0 条符合搜索条件'

    def _parse_search_result_page(self, soup):
        rslts = soup.find_all('a', 'B font_16')
        if not rslts:
            self.submit_search_no_results()
        for result in rslts:
            if '/content/' in result['href']:
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result.text
                )

    def _parse_parse_page(self, soup):
        for link in soup.select('strong.down_part_name a'):
            url = link['href']
            title = link.text.strip()
            season, episode = self.util.extract_season_episode(title)
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=url,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )
