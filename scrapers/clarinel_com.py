# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class Clarinel(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://www.clarinel.com'
    OTHERS_URLS = ["http://www.clarinel.com"]
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    SINGLE_RESULTS_PAGE = True

    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 200
        self.media_type_to_category = 'film 4, tv 6'
        # self.encode_search_term_to = 'utf256'
        # self.showposts = 0

    def _parse_search_result_page(self, soup):
        for link in soup.select('.dpad.searchitem b a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _fetch_no_results_text(self):
        return 'The search did not return any results.'

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))

    def _parse_parse_page(self, soup):
        title = soup.select_one('#news-title').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for code_box in soup.select('.goodpost'):
            text = str(code_box).replace('<br/>', ' ')
            for url in self.util.find_urls_in_text(text):
                if url.startswith('http'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=url,
                                             link_title=title,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )

        for link in soup.select('.goodpost a'):
            if not link.href.startswith(self.BASE_URL):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

        for link in soup.select('div.maincont pre code'):
            text = str(link).replace('<br/>', ' ')
            for url in self.util.find_urls_in_text(str(text)):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )
