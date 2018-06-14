# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ZhandiCc(SimpleScraperBase):
    BASE_URL = 'http://www.zhandi.cc'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ScraperBase.SCRAPER_TYPE_P2P, ]
    LANGUAGE = 'kor'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?s=vod-search'

    def _fetch_no_results_text(self):
        return u'您可以试试由百度提供的强大的站内搜索'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a[class="next pagegbk"]')
        if next_button:
            return self.BASE_URL + next_button.href
        return None

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self._fetch_search_url(search_term, media_type), data = {'wd' : search_term}, headers = {'Content-Type' : 'application/x-www-form-urlencoded'})
        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        results = soup.select('h5 a[target="_blank"]')

        if not results or len(results) == 0 :
            return self.submit_search_no_results()

        for result in soup.select('h5'):
            link = result.select_one('a[target="_blank"]')
            self.submit_search_result(
                link_url= self.BASE_URL + link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next() :
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('p.play-list a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url= self.BASE_URL + link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
