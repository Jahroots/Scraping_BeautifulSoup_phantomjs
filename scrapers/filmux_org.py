# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class FilmuxOrg(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://filmux.org'
    LONG_SEARCH_RESULT_KEYWORD = '2015'

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


    def _fetch_no_results_text(self):
        return u'Apgailestaujame, tačiau pagal jūsų paieškos frazę nieko nerasta'

    def _parse_search_result_page(self, soup):
        for link in soup.select('div.short-title h3 a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        for link in soup.select('div.video-responsive iframe'):
            if 'youtube' not in link['src']:
                redirect_soup = self.get_soup(link['src'])
                sources = redirect_soup.find('div', id='player').find_next('script').text
                files = self.util.find_urls_in_text(sources)
                for file in files:
                    if '.mp4' in file:
                        season, episode = self.util.extract_season_episode(file)
                        self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                 link_url=file,
                                                 link_title=title,
                                                 series_season=season,
                                                 series_episode=episode,
                                                 )
