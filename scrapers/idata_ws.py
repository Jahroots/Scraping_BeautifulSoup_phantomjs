# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class IData(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.idata.ws'
    OTHER_URLS = ['http://idata.ws', ]
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 20
        self.media_type_to_category = 'film 4, tv 5'
        # self.encode_search_term_to = 'cp1251'
        # self.showposts = 0

    def _fetch_no_results_text(self):
        return u'The search did not return any results'

    def _parse_search_result_page(self, soup):
        #if not soup.select('.btl a'):
        #    return self.submit_search_no_results()
        for link in soup.select('.btl a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2.btl')
        if title:
            title=title.text
        else:
            title = self.util.get_page_title(soup)
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('div.maincont a'):
            if not link.href.startswith(self.BASE_URL) and link.href.startswith('http'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

        for link in soup.select('div.maincont pre code'):
            for url in self.util.find_urls_in_text(str(link)):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )
