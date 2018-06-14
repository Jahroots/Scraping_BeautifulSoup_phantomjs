# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class Dostupnovsem(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://dostupnovsem.com'
    OTHER_URLS = []

    LONG_SEARCH_RESULT_KEYWORD = 'DVDRip'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'
        raise NotImplementedError('The domain is unavailable')

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 400
        self.media_type_to_category = 'film 1, tv 49'
        self.encode_search_term_to = 'cp1251'
        self.showposts = 0

    def get(self, url, **kwargs):
        return super(Dostupnovsem, self).get(url, allowed_errors_codes=[403],
                                               **kwargs)

    def post(self, url, **kwargs):

        return super(Dostupnovsem, self).post(url, allowed_errors_codes=[403], **kwargs)

    def _parse_search_result_page(self, soup):
        found = 0
        for res in soup.select('.topic'):
            self.submit_search_result(
                link_title=[el for el in res.previous_siblings if el.name == 'h1'][0].text,
                link_url=res.select_one('.afteranchor a').href
            )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('.shortnews h1').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.quote a'):
            if not link.href.startswith(self.BASE_URL) and \
                    not link.href.startswith('/'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

