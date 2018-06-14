# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class SerializmCom(SimpleScraperBase):
    BASE_URL = 'http://serializm.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search?searchtext={search_term}&submit=submit'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'не дал результатов'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('a.serial-item'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        files_links= self.util.find_file_in_js(soup.text)
        for files_link in files_links:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=files_link,
                link_title=files_link,
                series_season=series_season,
                series_episode=series_episode,
            )
