# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CacheableParseResultsMixin

class CooltvseriesCom(CacheableParseResultsMixin, SimpleScraperBase):
    BASE_URL = 'https://cooltvseries.com'
    OTHER_URLS = ['https://cooltvseries.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search.php?search={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'No Matching Shows Found'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.box'):
            link = result.select_one('a')
            ep_soup = self.get_soup(link.href)
            for ep_link in ep_soup.select('div.dwn-box ul li a'):
                self.submit_search_result(
                    link_url=ep_link.href,
                    link_title=ep_link.text,
                    image= self.BASE_URL + self.util.find_image_src_or_none(result, 'img'),
                )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.dwn-box a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
