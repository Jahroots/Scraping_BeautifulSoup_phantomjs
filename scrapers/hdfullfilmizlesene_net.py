# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class HdfullfilmizleseneNet(SimpleScraperBase):
    BASE_URL = 'http://www.hdfullfilmizlesene.tv'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return '{base_url}/page/{page}/?do=search&subaction=search&s={search_term}&searchbutton'.format(base_url=self.BASE_URL, search_term=search_term, page=start)

    def _fetch_no_results_text(self):
        return u'Hiç bir sonuç bulunamadı'

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
        for result in soup.select('div.anafilm'):
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
        for result in soup.select('div#pagelink a'):
            movie_link = self.get_soup(result['href']).select_one('div#kendisi iframe')['src']
            if not movie_link.startswith('http'):
                movie_link = 'http:'+movie_link
            if 'youtube' in movie_link:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_title=movie_link,
                series_season=series_season,
                series_episode=series_episode,
            )
