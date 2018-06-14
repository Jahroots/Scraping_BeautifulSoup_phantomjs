# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class FilmeserialeOnline(SimpleScraperBase):
    BASE_URL = 'https://filmeseriale.online'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rom'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    USERNAME = 'Signtearame'
    PASSWORD = 'uguu1Ootoo'
    EMAIL = 'patriciambarnes@dayrep.com'

    def setup(self):
        super(FilmeserialeOnline, self).setup()
        self._request_connect_timeout = 600
        self._request_response_timeout = 600


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Nu am gasit ce cautai,incearca din nou'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('h3.name a'):
            ep_soup = self.get_soup(results['href'])
            for episode_links in ep_soup.select('div.episode-title a')+soup.select('h3.name a'):
                title = episode_links.text + ' '+results.text
                season, episode = self.util.extract_season_episode(title)
                self.submit_search_result(
                    link_url=episode_links['href'],
                    link_title=title,
                    series_season=season,
                    series_episode=episode
                )
                found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(index_page_title)
        for link in soup.select('div#embed0 a'):
            movie_link = 'http' + link['href'].split('http')[-1]
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                series_season=season,
                series_episode=episode,
                link_text=title,
            )