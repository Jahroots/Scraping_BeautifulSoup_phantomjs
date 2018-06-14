# coding=utf-8

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Rodoved(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://www.rodoved.org'
    OTHERS_URLS = ['http://www.rodoved.org']
    LONG_SEARCH_RESULT_KEYWORD = 'mother'
    SINGLE_RESULTS_PAGE = True
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 200
        self.media_type_to_category = 'film 4, tv 6'
        # self.encode_search_term_to = 'cp1251'
        self.showposts = 1

    def _parse_search_result_page(self, soup):
        for result in soup.select('.searchitem h3 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('#news-title').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for lnk in soup.select('.maincont > div > div > div > a') + soup.select('.quote a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=self.BASE_URL + lnk.href if lnk.href.startswith('/') else lnk.href,
                                     link_title=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )
        for codeblock in soup.select('.scriptcode'):
            for link in self.util.find_urls_in_text(codeblock.text):
                link = self.BASE_URL + link if link.startswith('/') else link
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link
                                         )
