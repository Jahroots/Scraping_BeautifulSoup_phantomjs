# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Egexa(SimpleScraperBase):
    BASE_URL = 'http://movies.egexa.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        raise NotImplementedError('The site actually does not provide any real links. Only ads (and virii?).')

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type, start=0):
        self.start = start
        self.search_term = search_term
        self.media_type = media_type
        return self.BASE_URL + '/movies/list.php?q={}'.format(search_term)

    def _fetch_next_button(self, soup):
        next = soup.select_one('img', alt="Next Page")
        self.log.debug('----------------')
        return next.parent.href if next else None

    def _fetch_no_results_text(self):
        return u'The search did not return any results'

    def _parse_search_result_page(self, soup):
        for result in soup.select("#MainSection table ul li a"):
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
