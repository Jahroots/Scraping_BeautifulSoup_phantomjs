# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, SimpleGoogleScraperBase



class FilmSerialSk(SimpleGoogleScraperBase, SimpleScraperBase):
    BASE_URL = 'https://www.film-serial.sk'
    OTHER_URL = ['http://www.film-serial.sk']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'slo'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL,
        )
        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _parse_parse_page(self, soup):
        if '/products/' in soup._url:
            index_page_title = self.util.get_page_title(soup)
            iframes = soup.find('div', 'wrapperText').find_all('iframe')
            for iframe in iframes:
                source_url = iframe['src']
                if 'http' not in source_url:
                    source_url = 'http:'+source_url
                season, episode = self.util.extract_season_episode(soup._url)
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=source_url,
                                         series_season=season,
                                         series_episode=episode
                                         )
