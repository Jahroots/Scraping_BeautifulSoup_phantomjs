# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class TorrentlocuraCom(SimpleScraperBase):
    BASE_URL = 'http://torrentlocura.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/buscar'

    def _fetch_no_results_text(self):
        return u'Sorry, we could not find the movie that you were looking for this movie'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Next')
        return next_link['href'] if next_link else None

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self._fetch_search_url(search_term, media_type), data = {'q' : search_term})

        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):

        found = 0
        for results in soup.select('ul.buscar-list li'):
            title = results.text
            url = results.select_one('a')
            if url:
                url = url['href']
                self.submit_search_result(
                            link_url= url,
                            link_title=title,
                )
                found = 1
        if not found:
            return self.submit_search_no_results()

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1 strong').text
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(index_page_title)
        for link in soup.find_all('div', 'box5'):
            url = link.find('a')['href']
            if 'javascript' not in url:
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url= url,
                                         series_season=season,
                                         series_episode=episode,
                                         link_title=title
                                         )
        torrent = soup.select_one('a.btn-torrent')['href']

        if 'javascript' not in torrent:
            torrent_url = self.get_redirect_location(self.get_redirect_location(torrent))
            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=torrent_url,
                                     series_season=season,
                                     series_episode=episode,
                                     link_title=title
                                     )
