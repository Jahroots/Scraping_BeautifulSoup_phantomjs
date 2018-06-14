# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class M4ufreeInfo(SimpleScraperBase):
    BASE_URL = 'http://m4ufree.info'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return '{base_url}/tag/{search_term}/{page}'.format(base_url=self.BASE_URL, search_term=search_term, page=start)

    def get(self, url, **kwargs):
        return super(M4ufreeInfo, self).get(url, allowed_errors_codes=[404, ], **kwargs)

    def _fetch_no_results_text(self):
        return u'We found nothing'

    def _parse_search_results(self, soup):
        if not soup.select('div.image'):
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
        for result in soup.select('div.image'):
            link = self.get_soup(result.select_one('a').href).select_one('div.detail ol > li a')
            if link:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h4')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text.split(':')[-1])
        for result in soup.select('span.btn-eps'):
            movie_link = self.get_redirect_location('http://m4ufree.info/view.php?v='+result['link'])
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_title=movie_link,
                series_season=series_season,
                series_episode=series_episode,
            )
