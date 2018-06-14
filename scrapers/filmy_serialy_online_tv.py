# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import re


class FilmySerialyOnlineTv(SimpleScraperBase):
    BASE_URL = 'https://filmy-serialy-online.tv'
    OTHERS_URLS = ['http://filmy-serialy-online.tv']
    LANGUAGE = 'slo'
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'man'


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH,
                          self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING,
                          self.BASE_URL)
        self._request_connect_timeout = 300
        self._request_response_timeout = 600
        self._request_size_limit = (1024 * 1024 * 20)

    def _fetch_no_results_text(self):
        return u'Žiadny záznam.'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?menu=find&search={}&search_typ=&search_rok=&all=1'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        link = ''
        try:
            link = soup.find('ul', 'pagination').find('i', 'fa fa-long-arrow-right').find_previous('a')['href']
        except AttributeError:
            pass
        if link:
            return link

    def _parse_search_result_page(self, soup):
        table_rows = soup.find(text=re.compile(u'Približný počet výsledkov')).find_next('table').find_all('tr')[1:]
        for table_row in table_rows:
            try:
                for table in table_row.find_all('table', attrs={'style':'width:150px;height:20px'}):
                    link = table.find('td', attrs={'style': 'text-align:center'}).find('a')
                    self.submit_search_result(
                        link_url=self.BASE_URL+ link['href'],
                        link_title=link.text,
                    )
            except AttributeError:
                pass


    def _parse_parse_page(self, soup):
        online_link = soup.select_one('a[href*="/video/"]')['href']
        url_soup =  self.get_soup(self.BASE_URL+online_link)
        iframe = url_soup.find('iframe', 'center')
        if iframe:
            url = iframe['src']
            title = self.util.get_page_title(url_soup)
            season, episode = self.util.extract_season_episode(title)
            self.submit_parse_result(index_page_title=title,
                                     series_season=season,
                                     series_episode=episode,
                                     link_url=self.BASE_URL + url)
