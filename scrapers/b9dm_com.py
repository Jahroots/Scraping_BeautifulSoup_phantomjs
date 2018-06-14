# coding=utf-8

import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class b9dmCom(SimpleScraperBase):
    BASE_URL = 'http://b9good.com'
    OTHER_URLS = ['http://b9dm.com', 'http://up.b9dm.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'jap'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return None

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup('http://up.b9dm.com/index.php/search', data = {'keyword' : search_term,
        'key': 'title'})
        self._parse_search_result_page(soup)

    def _fetch_no_results_text(self):
        return u'No video found'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text='>')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class*="main"] dl.t_box a.pic')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            if 'cosplay' not in result.href:
                self.submit_search_result(
                    link_url=result.href,
                    link_title=result.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.caption h3')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div#dl a'):
            if 'http' in link.text:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        script = soup.select_one('div#swfplayer script')
        url = re.search("""url=\"(.*)\";""", script.text)
        if url:
            url = url.group(1)
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=url,
                series_season=series_season,
                series_episode=series_episode,
            )
