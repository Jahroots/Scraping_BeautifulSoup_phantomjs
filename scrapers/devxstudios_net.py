# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class DevxStudios(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://devxstudim.org'
    OTHER_URLS = ['http://devxstudiv.org', "http://devxstudios.net"]

    LONG_SEARCH_RESULT_KEYWORD = 'Queen'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        # Site also has "Music"
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return "The search did not return any results."

    def _parse_search_result_page(self, soup):
        for item in soup.select('.baseer'):
            self.submit_search_result(link_url=item.select_one('.arg.bs_author a').href,
                                      link_title=item.select_one('h1').text)

    def _parse_parse_page(self, soup, **kwargs):
        title = soup.title.text.split(u' » ')[0].strip()
        series_season, series_episode = self.util.extract_season_episode(title)

        for box in soup.select('.quote')+soup.find_all('div', align="center"):

            text = str(box).replace('<br/>', ' ')

            for url in self.util.find_urls_in_text(text):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )
