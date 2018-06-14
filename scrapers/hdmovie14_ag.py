# coding=utf-8
import base64
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class Hdmovie14Ag(SimpleScraperBase):
    BASE_URL = 'http://www1.solarmovie.net'
    OTHER_URLS = ['http://solarmovie.net', 'http://hdmovie14.ag']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search-movies/{search_term}.html'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u'»')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.ml-item'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for results in soup.select('div.server_line'):
            try:
                movie_link = self.make_soup(base64.decodestring(self.get_soup(results.select_one('a').href).
                                                                select_one('div#media-player script').text.split('("')[-1].
                                                                split('")')[0])).select_one('iframe')['src']
            except AttributeError:
                movie_link = self.get_soup(results.select_one('a').href).select_one('div#media-player a')['href']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_title=movie_link,
                series_season=series_season,
                series_episode=series_episode,
            )
