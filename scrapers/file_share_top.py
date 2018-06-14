# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FileShareTop(SimpleScraperBase):
    BASE_URL = 'http://file-share.top'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cze'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return u'Celkem nalezeno 0 záznamů'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search?q=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = ''
        try:
            link = soup.find('ul', 'pagination').find('i', 'fa fa-long-arrow-right').find_previous('a')['href']
        except AttributeError:
            pass
        if link:
            return link

    def _parse_search_result_page(self, soup):
        table_row = soup.find_all('div', 'file-title')
        for link in table_row:
             if '?q=' in link.a['href']:
                 continue
             self.submit_search_result(
                link_url=link.a['href'],
                link_title=link.a.text,
            )

    def _parse_parse_page(self, soup):
        url = soup.find('a', 'btn btn-success btn-lg download-button')['href']
        if 'http' not in url:
            url=self.BASE_URL + url
        title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        self.submit_parse_result(index_page_title=title,
                                 series_season=season,
                                 series_episode=episode,
                                 link_url=url)
