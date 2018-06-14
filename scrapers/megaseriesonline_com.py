#coding=utf-8
from sandcrawler.scraper import SimpleScraperBase, VideoCaptureMixin

class MegaSeriesOnline(SimpleScraperBase):

    BASE_URL = 'http://www.loveseriesonline.com'
    OTHER_URLS = ['http://megaseries.online','http://www.megaseriesonline.com']
    SINGLE_RESULTS_PAGE = True

    USER_AGENT_MOBILE = False
    LONG_SEARCH_RESULT_KEYWORD = 'The'
    TRELLO_ID = 'MguKn8ZP'

    def setup(self):
        self.register_scraper_type(SimpleScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(SimpleScraperBase.MEDIA_TYPE_FILM)
        self.register_media(SimpleScraperBase.MEDIA_TYPE_TV)
        self.register_url(SimpleScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(SimpleScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self.register_url(SimpleScraperBase.URL_TYPE_SEARCH, 'http://seriesplay.net')
        self.register_url(SimpleScraperBase.URL_TYPE_LISTING, 'http://seriesplay.net')


    def _fetch_search_url(self, search_term, media_type):
        self.page = 1
        return u'{}/search?q={}'.format(
            self.BASE_URL,
            self.util.quote(search_term)
        )

    def _fetch_next_button(self, soup):
        return None

    def _fetch_no_results_text(self):
        return u'Nenhuma postagem correspondente para a consulta'

    def _parse_search_result_page(self, soup):
        self.log.debug(soup)
        results = soup.select('h3[class="post-title entry-title"]')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for link in results:
            link = link.select_one('a')
            self.submit_search_result(
                        link_url=link.href,
                        link_title=link.text,
                )



    def _parse_parse_page(self, soup):
        title = soup.title.text

        iframe = soup.select_one('iframe[src]')
        if iframe:
            self.submit_parse_result(
                       index_page_title=self.util.get_page_title(soup),
                       link_url=iframe['src'],
                       link_title=title
            )
