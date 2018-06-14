# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class G1filmesGratis(SimpleScraperBase):
    BASE_URL = 'http://www.g1filmes.org'
    OTHER_URLS = [
        'http://www.g1filmes.net',
        'http://www.g1filmesgratis.com',
        'http://www.g1filmes.com',
        'http://www.meulinkprotegido.com',
        'http://www.baixarfilmesdegraca.com'
    ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'por'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True

    def search(self, search_term, media_type, **extra):
        self.webdriver().get(self.BASE_URL + '/?s={}'.format(search_term) )
        soup = self.make_soup(self.webdriver().page_source)

        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):

        results = soup.select('.entry-title a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for link in results:
            if link and link.has_attr('href'):
                self.submit_search_result(
                    link_title=link.text,
                    link_url=link.href
                )

        next_button = self._fetch_next_button(soup)
        self.log.warning(next_button)
        if next_button and self.can_fetch_next():
            self.webdriver().get(next_button)
            self._parse_search_result_page(self.make_soup(self.webdriver().page_source))

    def _fetch_no_results_text(self):
        return u'Desculpe, mas nada foi encontrado!'

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        next_link = soup.select_one('.nextpostslink')
        return next_link.href if next_link else None

    def parse(self, parse_url, **extra):
        self.webdriver().get(parse_url)
        soup = self.make_soup(self.webdriver().page_source)
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):

        title = soup.select_one('.entry-title').text
        series_season, series_episode = self.util.extract_season_episode(title)

        for link in soup.select('.entry-content div a'):

            if link.href.startswith(self.BASE_URL):
                continue

            link = self.get_redirect_location(link.href.split('?u=')[1].split('"')[0][::-1]
                                              if '?u=' in link.href
                                              else link.href)

            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link,
                                     link_title=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )

