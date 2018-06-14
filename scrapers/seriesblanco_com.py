# -*- coding: utf-8 -*-
import re
from sandcrawler.scraper import SimpleScraperBase

class SeriesBlanco(SimpleScraperBase):
    BASE_URL = 'https://seriesblanco.com'
    OTHERS_URLS = ['http://seriesblanco.com']
    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def setup(self):
        self.register_scraper_type(SimpleScraperBase.SCRAPER_TYPE_OSP)
        self.register_media(SimpleScraperBase.MEDIA_TYPE_FILM)
        self.register_media(SimpleScraperBase.MEDIA_TYPE_TV)

        self.register_url(SimpleScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(SimpleScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.search_term_language = 'spa'


    def get(self, url, **kwargs):
        return super(SeriesBlanco, self).get(
            url,allowed_errors_codes=[404],  **kwargs)

    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        self.search_term = search_term
        return self.BASE_URL + '/search.php?q1=' +'%s' % self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=re.compile('>>'))
        self.log.debug('------------------------')
        return self.BASE_URL + '/search.php?q1=%s' % self.util.quote(self.search_term) + link['href'].replace('?', '&') if link else None

    def _parse_search_result_page(self, soup):
        found=0
        series = soup.select('ul[class="nav navbar-nav"] li')

        if not series or len(series) == 0:
           return self.submit_search_no_results()

        series = soup.select('ul[class="nav navbar-nav"] li')
        for serie in series:
            serie_link = serie.select_one('a')

            soup = self.get_soup(self.BASE_URL + serie_link['href'].replace('..', ''))
            episodes = soup.select('tr.table-hover a[type="button"]')

            found = 1
            for episode in episodes:

                self.submit_search_result(
                        link_url = self.BASE_URL + episode['href'],
                        link_title = soup.select_one('h3.panel-title').text
                )

        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):

        links = soup.select('div[class="grid_content sno"] span a')
        for link in links:
            id = link.href.split('/')[-5].replace('enlace', '')
            serie = link.href.split('/')[-4]
            temp = link.href.split('/')[-3]
            cap = link.href.split('/')[-2]

            xhr_link = self.BASE_URL + '/ajax/load_enlace.php?serie={}&temp={}&cap={}&id={}'.format(serie, temp,
                                                                                                           cap, id)
            xhr_soup = self.get_soup(xhr_link)
            input = xhr_soup.select_one('input[onclick*="window.open"]')
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=input['onclick'].replace('window.open("', '').replace('");', '').strip(),
                link_title=soup.select_one('h3[class="panel-title"]').text
            )

