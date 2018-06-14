# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FileGe(SimpleScraperBase):
    BASE_URL = 'http://www.file.ge'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'geo'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type=None):
        self.page = 1
        return '{base_url}/index.php?s={search_term}&sbutt=წინ'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_next_button(self, soup):
        self.page += 1
        pagebar = soup.select_one('div.pagebar')
        if pagebar:
            next_page = pagebar.find('a', text=self.page)
            if next_page:
                return next_page.href
        return None

    def _fetch_no_results_text(self):
        return u'თქვენს მიერ მითითებულ საძიებო სიტყვაზე არაფერი მოიძებნა'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.entry'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h3')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        result = soup.find('div', 'entrybody').find_all('a')
        for movie_link in result:
            if movie_link.select_one('strong'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link.href,
                    link_title=movie_link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        player_link = soup.find('div', 'entry ').find('div', 'entrybody').find('param', attrs={'name':'flashvars'})
        if player_link:
            link = re.search("""file=(.*)""", player_link['value']).group(1)
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_title=link,
                series_season=series_season,
                series_episode=series_episode,
            )
