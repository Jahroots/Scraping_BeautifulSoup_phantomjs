# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class TremendaSeries(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://tremendaseries.com/'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.webdriver_type = 'phantomjs'
        self.requires_webdriver = True

        raise  NotImplementedError('Website not longer required.')

    def _fetch_search_url(self, search_term, media_type, start=None):
        return self.BASE_URL + 'resultados/' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):

        results = soup.select('div.portada a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            soup = self.get_soup(result['href'])
            image = result.select_one('img')
            episodes = soup.select('div.tit_enlacess ul li a')
            for episode in episodes:
                self.submit_search_result(
                    link_url = episode['href'],
                    link_title = episode.text,
                    image = image['src']
                )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('a.menu'):
            href = link['href']
            href = href.split('enlace=')[1]
            href = href.replace('&columna=ver','').strip()
            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url=href,
                link_title=title,
                series_season=season,
                series_episode=episode
            )
