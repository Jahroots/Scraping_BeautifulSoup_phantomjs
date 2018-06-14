# coding=utf-8

import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class KinoxTv(SimpleScraperBase):
    BASE_URL = 'https://kinox.tv'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'deu'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/Search.html?q={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'0 bis 0 von 0 Einträgen'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        find = 0
        for results in soup.select('td.Title a'):
            result = self.BASE_URL+results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            find=1
        if not find:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        download_links= soup.select('ul#HosterList li')
        for download_link in download_links:
            stream = json.loads(self.get('https://kinox.tv/aGET/Mirror/'+download_link['rel']).text)

            movie_soup = self.make_soup(stream['Stream'])
            try:
                source = movie_soup.find('iframe')['src']
            except TypeError:
                source = movie_soup.find('a')['href']


            if 'http' not in source:

                source = 'http:' + source
            if '/Out/?s' in source:
                source = source.split('?s=')[-1]
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=source,
                link_text=title,
            )
