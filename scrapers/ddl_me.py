# coding=utf-8

import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class DdlMe(SimpleScraperBase):
    BASE_URL = 'http://en.ddl.me'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search_99/?q={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Not Found'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        find = 0
        for results in soup.select('div#view a.item'):
            result = results['href']
            title = results['title']
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            find=1
        if not find:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1#itemType').text.strip()
        index_page_title = self.util.get_page_title(soup)
        id_num = soup.find('div', id='rlsNav')['class'][-1].split('_')[-1]
        links_dict = json.loads(soup.text.split('ar subcats = ')[-1].split('; var mtype')[0])
        available_links = None
        try:
            available_links = links_dict[id_num]['links']
        except KeyError:
            pass
        if available_links:
            for lst in links_dict[id_num]['links']:
                for download_link in links_dict[id_num]['links'][lst]:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=download_link[3],
                        link_text=title,
                    )

class DeDdlMe(DdlMe):
    BASE_URL = 'http://de.ddl.me'
    LANGUAGE = 'deu'
