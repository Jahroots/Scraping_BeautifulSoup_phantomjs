# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import json


class OnlineMultfilmyRu(SimpleScraperBase):
    BASE_URL = 'http://onlinemultfilmy.ru'
    LONG_SEARCH_RESULT_KEYWORD = '20'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Ничего не найдено по запросу'

    def _fetch_next_button(self, soup):
        return self.util.get_href_or_none(soup, '.nextpostslink')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/%s' % self.util.quote(search_term)

    def _parse_search_result_page(self, soup):
        for result in soup.select('.mainlink'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.post h1')
        if title and title.text:
            title = title.text

        videos = soup.text.split('"SERIES_LIST":')
        if videos and len(videos) > 1 :
            json_string = videos[1].split('}')[0].strip()
            for video in json.loads(json_string.replace(',]', ']'))[0]:
                link = video.split('|')[0].strip()
                if link and len(link) > 0:
                    if link.find('http:') == -1:
                        link = 'http:' + link

                    self.submit_parse_result(
                        index_page_title= self.util.get_page_title(soup),
                                             link_url= link,
                                             link_text = title
                                             )

        for iframe in soup.select('iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url='http:' + iframe['src'] if iframe['src'].startswith('//')
                                     else iframe['src'],
                                     )
