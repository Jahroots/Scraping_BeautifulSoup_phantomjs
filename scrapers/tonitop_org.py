# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class Tonitop(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://www.tonitop.org'
    OTHER_URLS = ['http://www.tonitop.org']
    LONG_SEARCH_RESULT_KEYWORD = '2012'
    SINGLE_RESULTS_PAGE = True
    USER_AGENT_MOBILE = False

    def get(self, url, **kwargs):
        return super(Tonitop, self).get(url, allowed_errors_codes=[403, ], **kwargs)

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
        self.bunch_size = 400
        self.media_type_to_category = 'film 4, tv 6'
        # self.encode_search_term_to = 'cp1251'
        # self.showposts = 0

    def _parse_search_result_page(self, soup):
        for link in soup.select('.entrytitle h3 a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.entrytitle h3 a').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.entrytext div div a'):
            if 1 : #not link.not_local(self.BASE_URL) and link.startswith_http:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=self.get_redirect_location(
                                             self.BASE_URL + link.href) if link.href.startswith(
                                             '/file/go.php') else link.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

        for box in soup.select('.entrytext div div')+soup.select('.scriptcode'):
            if 1: #box.attrs.get('align') == 'CENTER':
                for url in self.util.find_urls_in_text(str(box)):
                    if 'http'  in url:
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=url,
                                             link_title=title,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )
