# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class HugeWarez(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://hugewarez.net'
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        # OpenSearchMixin advanced search settings
        #self.bunch_size = 10
        self.media_type_to_category = 'film 2, tv 2'
        # self.encode_search_term_to = 'utf256'
        #self.showposts = 0

    def _fetch_no_results_text(self):
        return u'The search did not return any results'

    def _parse_search_result_page(self, soup):
        for result in soup.select(".dpad.searchitem h3 a"):
            self.submit_search_result(link_title=result.text,
                                      link_url=result.get('href'))

    def _parse_parse_page(self, soup):
        title = soup.select_one('h3.btl').text
        series_season, series_episode = self.util.extract_season_episode(title)

        code_box = soup.select_one('.maincont pre code')
        if code_box:
            for url in self.util.find_urls_in_text(code_box.text):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

        for url in soup.select('.quote a'):
            if url.startswith_http and not 'http://sharingarena.com/register.html' == url.href:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )
        for url in self.util.find_urls_in_text(unicode(soup.select_one('div.maincont'))):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=url,
                                     link_title=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )