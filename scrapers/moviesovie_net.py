# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class MovieSovie(SimpleScraperBase):
    BASE_URL = 'http://moviesovie.net'
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        # self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        raise NotImplementedError('Deprecated')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/download.php?search=' + search_term

    def _fetch_no_results_text(self):
        return u'Ningún resultado encontrado, por favor intentelo nuevamente'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('a.movie__title.link--huge')
        if not results:
            self.submit_search_no_results()

        for link in results:
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.title)

    def _parse_parse_page(self, soup):
        try:
            title = soup.select_one('.fn').text.strip()
            # series_season, series_episode = self.util.extract_season_episode(title)

            for link in soup.select('.download.col-md-12 a'):
                if not link.href.startswith('magnet'):
                    url = link['href'] if link['href'].startswith('http') else 'http:' + link['href']
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=url,
                                             link_text=title,
                                             # series_season=series_season,
                                             # series_episode=series_episode,
                                             )
        except AttributeError as e:
            pass  # self.show_in_browser(soup)
            # raise
