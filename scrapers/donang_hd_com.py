# coding=utf-8
import base64
import urllib
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class DonangHdCom(SimpleScraperBase):
    BASE_URL = 'https://www.donang-hd.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tai'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'1/0'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.loadnavi')
        if next_button:
            return next_button.href
        return None

    def _parse_search_results(self, soup):
        if not soup.select('div.movie-poster'):
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        next_button_link = self._fetch_next_button(soup)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.movie-poster'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href.encode('utf-8'),
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('table#table-play form input[name="codeurl"]'):
            movie_link = base64.decodestring(link['value'])
            url = urllib.unquote(movie_link)
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
