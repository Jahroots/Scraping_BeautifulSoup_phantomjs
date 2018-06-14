# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class MiraloGratis(SimpleScraperBase):
    BASE_URL = 'http://miralogratis.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403,], **kwargs)

    def _fetch_no_results_text(self):
        return u'No se encontró lo que buscaba.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Siguiente »')
        self.log.debug('-' * 30)
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('article a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.sinp.ovhd.mbot10px h2 a')
        if title:
            title = title.text
            season, episode = self.util.extract_season_episode(title)

        for vid in soup.select('div[class*="tab-pane"] iframe'):
            try:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=vid.get('src') or vid['data-src'],
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )
            except Exception as e:
                self.log.exception(e)
                #self.show_in_browser(soup)
                raise e



