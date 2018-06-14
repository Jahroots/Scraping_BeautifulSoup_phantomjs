# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class AnzhuotanCom(SimpleScraperBase):
    BASE_URL = 'http://www.anzhuotan.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ScraperBase.SCRAPER_TYPE_P2P, ]
    LANGUAGE = 'zho'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Blocked')
        super(self.__class__, self).setup()
        self._request_connect_timeout = 900
        self._request_response_timeout = 600

    def _do_search(self, search_term):
        return self.post_soup(

            self.BASE_URL + '/?s=vod-search',
            data={
                'wd':search_term})

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(self._do_search(search_term))

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('a.list-img'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
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
        for result_list in soup.select('a.labe2'):
            result_soup = self.get_soup(self.BASE_URL+result_list.href)
            torrent_urls = result_soup.select('input[name="down_url_list_0"]')
            for torrent_url in torrent_urls:
                torrent_url = torrent_url['value']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=torrent_url,
                    link_title=torrent_url,
                    series_season=series_season,
                    series_episode=series_episode,
                )
            link = result_soup.select_one('a#li-a')
            if link:
                self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
                )
