# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, VideoCaptureMixin
from sandcrawler.scraper.caching import cacheable

from pyamf.remoting.client import RemotingService

import json, re


class NezzsorozatokatInfo(SimpleScraperBase):
    BASE_URL = 'http://nezzsorozatokat.info'

    LONG_SEARCH_RESULT_KEYWORD = '2016'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "hun"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)



    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/js/autocomplete_ajax.php?term={}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        ajax_text = json.loads(soup.text)
        for movies in ajax_text:
            if not movies['value']:
                return self.submit_search_no_results()
            # Only submit links that have an episode attached to them, not the
            # roots.
            if 'e=' in movies['id']:
                self.submit_search_result(
                        link_url=self.BASE_URL+'/?'+movies['id'],
                        link_title=movies['label'].strip(),
                    )

    def _parse_parse_page(self, soup):


        divs = soup.find_all('div', attrs={'load-id':re.compile(r'\d+')})
        index_title = self.util.get_page_title(soup)
        title = soup.select_one('h1').text
        id = soup.select_one('div[sorsz]')

        if id:
            id = id['sorsz']

            result_urls = self._extract_video_belt(id, soup._url)
            if result_urls:
                for result_url in result_urls:
                                self.submit_parse_result(
                                    link_url=result_url,
                                    index_page_title=index_title,
                                    link_text=title,
                                )

    @cacheable()
    def _extract_video_belt(self, div_id, last_url):
        page_url = self.BASE_URL + '/videobetolt.php?id={}&ad=1'.format(div_id)
        self.log.debug(last_url)
        source = self.get_soup(page_url, headers= {'Referer' : last_url})
        self.log.debug(source)
        iframe = source.find('iframe')
        if iframe:
            return [iframe['src'], ]
        else:
            return None




