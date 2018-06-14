# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class Fulldiziizleyelim2Com(SimpleScraperBase):
    BASE_URL = 'http://www.fulldiziizleyelim2.com'
    OTHER_URLS = ['http://www.fulldiziizleyelimm.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USER_AGENT_MOBILE = False

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return '{base_url}/etiket/{search_term}-{page}.html'.format(base_url=self.BASE_URL, search_term=search_term, page=start)

    def _fetch_no_results_text(self):
        return u'Lütfen tekrar deneyiniz'

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.product-box'):
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
        for result in soup.select('div.kisim-selected')+soup.select('div.kisim-top'):
            for movie_link in self.get_soup(self.BASE_URL+result.select_one('a').href).select('div.video-box iframe'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link['src'],
                    link_title=movie_link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
