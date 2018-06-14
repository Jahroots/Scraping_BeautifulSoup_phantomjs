# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class CineCinema(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://cinecinema.org'
    OTHER_URLS = []
    LONG_SEARCH_RESULT_KEYWORD = u'жизнь'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_TV)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 20
        self.media_type_to_category = 'film 0, tv 0'
        self.encode_search_term_to = 'cp1251'
        # self.showposts = 0

    def _parse_search_result_page(self, soup):
        for link in soup.select('.title_spoiler h1 a'):
            self.submit_search_result(
                link_title=link.text.strip(),
                link_url=link.href
            )


    def _fetch_search_url(self, search_term):
        return self.BASE_URL + '/index.php?name=search'

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов'

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))

    def _parse_parse_page(self, soup):
        try:
            title = soup.select_one('#news-title').text
            # series_season, series_episode = self.util.extract_season_episode(title)

            for link in soup.select('.quote a'):
                if not link.text.startswith(self.BASE_URL) and link.text.startswith('http'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link.text,
                                             link_title=title,
                                             # series_season=series_season,
                                             # series_episode=series_episode,
                                             )
        except:
            pass
