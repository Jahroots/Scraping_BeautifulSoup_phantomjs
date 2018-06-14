# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class WatchOnlineCartoons(SimpleScraperBase):
    BASE_URL = "http://www.watchonlinecartoons.net"
    OTHER_URLS = []

    LONG_SEARCH_RESULT_KEYWORD = 'zero'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return 'Sorry, but you are looking for something that isn\'t here'

    def _fetch_next_button(self, soup):
        nxt = soup.select_one('.nav-next > a')
        self.log.debug('---------------')
        return nxt.href if nxt else None

    def _parse_search_result_page(self, soup):
        results = soup.select('h2 a')
        if not results:
            self.submit_search_no_results()

        for result in results:
            self.submit_search_result(link_title=result.text,
                                      link_url=result.href)

    def _parse_parse_page(self, soup, depth=0):
        title = soup.select_one('.post-info h1').text
        season, episode = self.util.extract_season_episode(title)

        # flashvars = soup.find('param', name='flashvars')['value']
        # print soup.find('meta', itemprop="contentUrl")
        try:
            contentUrl = soup.find('meta', itemprop="contentUrl")['content']

            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=self.util.unquote(contentUrl),
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode)
        except:
            pass
