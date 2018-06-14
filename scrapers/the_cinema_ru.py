# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin


class TheCinemaRu(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://the-cinema.org'
    OTHER_URLS = ['http://the-cinema.net', 'http://the-cinema.ru', ]
    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = '5N2Vc5mP'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ]  + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _parse_search_result_page(self, soup):
        for result in soup.select('h2.heading a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.heading').text.strip()
        for link in soup.select('iframe'):
            if 'youtube' in link['src']:
                continue
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link['src'],
                link_title=title,
            )
        torrent_link = soup.find('img', attrs={'title':'Скачать торрент '}).find_previous('a')['href']
        if 'http' not in torrent_link:
            return
        self.submit_parse_result(
            index_page_title=self.util.get_page_title(soup),
            link_url=torrent_link,
            link_title=title,
        )
