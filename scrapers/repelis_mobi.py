# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class RepelisMobi(SimpleScraperBase):
    BASE_URL = 'https://repelis.mobi/'
    OTHER_URLS = ['http://repelis.mobi']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type=None):
        self.page = 1
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL,
            search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Contenido no disponible'

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)

        self.page += 1
        for link in soup.select('div#paginador ul li a'):
            if link.text == str(self.page):
                self._parse_search_results(
                    self.get_soup(
                        link.href
                    )
                )

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.item'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.movieplay iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
