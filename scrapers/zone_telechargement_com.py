# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class ZoneTelechargement(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.zone.telechargementz.tv'

    # LONG_SEARCH_RESULT_KEYWORD = 'dvdscr'

    def setup(self):
        raise NotImplementedError('Duplicate - refer to telechargmentz.tv')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


    def _fetch_no_results_text(self):
        return u'La recherche n a retourné aucun résultat.'

    def _parse_search_result_page(self, soup):

        for result in soup.select('div.post-title'):
            link = result.select_one('a')
            if link:
                self.submit_search_result(
                    link_url=link.href,
                    link_title= result.text
                )

    def _parse_parse_page(self, soup):
        title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)

        links = soup.select('a[href*="http://security-links.com"]')

        for link in links:
            soup = self.get_soup(link.href)
            link = soup.select_one('#hideshow a')
            self.submit_parse_result(index_page_title=title,
                                     link_url=link.href,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )
