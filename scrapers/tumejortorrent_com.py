# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TumejortorrentCom(SimpleScraperBase):
    BASE_URL = 'http://tumejortorrent.com'
    OTHER_URLS = ['http://www.tumejortorrent.com']

    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        super(self.__class__, self).setup()
        self._request_connect_timeout = 300
        self._request_response_timeout = 600

    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?page=buscar&url=&letter=&q={}&categoryID=&categoryIDR=&calidad=&idioma=' \
                               '&ordenar=&inon=&'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        next_link = soup.find('ul', 'pagination')
        if next_link:
            next_link = next_link.find('a', text=u'Next')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        blocks = soup.find_all('div', 'info')
        any_results = False
        for block in blocks:
            link = block.find('a')['href']
            title = block.find('a').text
            self.submit_search_result(
                    link_url=link,
                    link_title=title,
                )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(index_page_title)
        for link in soup.find_all('a', id='descargar'):
             self.submit_parse_result(index_page_title=index_page_title,
                                      link_url=link['href'],
                                      series_season=season,
                                      series_episode=episode
                                                )
        torrent = soup.select_one('a.btn-torrent')['href']
        torrent_url = self.get_redirect_location(self.get_redirect_location(torrent))
        self.submit_parse_result(index_page_title=index_page_title,
                                 link_url=torrent_url,
                                 series_season=season,
                                 series_episode = episode
                                 )
