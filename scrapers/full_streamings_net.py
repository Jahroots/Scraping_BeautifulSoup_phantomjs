# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FullStreamings(SimpleScraperBase):
    BASE_URL = "http://www.full-streamings.net"
    OTHER_URLS = []

    LONG_SEARCH_RESULT_KEYWORD = 'rock'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

            # self.long_parse = True
        raise NotImplementedError('Website no longer available')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/movie/{}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return

    def _fetch_next_button(self, soup):
        return

    def _parse_search_result_page(self, soup):
        results = soup.select('#inner_content_body h2 b u a')
        if not results:
            self.submit_search_no_results()

        for result in results:
            self.submit_search_result(link_title=result.text,
                                      link_url=result.href)

    def _parse_parse_page(self, soup, depth=0):
        title = soup.select_one('#inner_content_body h1').text
        season, episode = self.util.extract_season_episode(title)

        watchfull_lnk = soup.select_one('.play')
        if watchfull_lnk and '//ads.ad-center.com' not in watchfull_lnk:
            url = watchfull_lnk.href
            if ':ptth' in url:
                url = url[37:][::-1]

            if self.BASE_URL in url:
                self._parse_iframes(
                    self.get_soup(url),
                    link_title=title,
                    series_season=season,
                    series_episode=episode)
            else:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode)
