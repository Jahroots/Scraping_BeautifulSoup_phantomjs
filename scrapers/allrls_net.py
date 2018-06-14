# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class AllrlsNet(SimpleScraperBase):
    BASE_URL = 'http://allrls.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('The website is deprecated')

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?go=Search&s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Nothing Found'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u'Next Entries »')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('h2.entry-title'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div.entry-content a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
