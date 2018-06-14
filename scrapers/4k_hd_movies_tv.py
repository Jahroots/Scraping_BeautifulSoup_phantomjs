# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class _4k_hd_movies(SimpleScraperBase):
    BASE_URL = 'https://4k-hd-movies.tv'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'ger'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Nichts gefunden'

    def _fetch_next_button(self, soup):
        link = soup.select_one('.nav-previous a')
        self.log.debug('-' * 30)
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.comments-link a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.entry-content p span').text

        season, episode = self.util.extract_season_episode(title)

        for vid in soup.select('.eintrag_download'):
            try:
                if vid.parent.startswith_http:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=vid.parent.href,
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )
            except Exception as e:
                self.log.exception(e)
                # self.show_in_browser(soup)
                raise e
