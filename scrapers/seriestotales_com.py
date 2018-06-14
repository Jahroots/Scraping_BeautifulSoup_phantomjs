# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SeriesTotales(SimpleScraperBase):
    BASE_URL = 'http://seriestotales.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        #self.webdriver_type = 'phantomjs'
        #self.requires_webdriver = ('parse', )

        self.long_parse = True

    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?q=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Siguiente')
        self.log.debug('------------------------')
        return self.BASE_URL + "/" + link['href'] if link else None

    def _parse_search_result_page(self, soup):

        results = soup.select('a[data-num]')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            image = result.select_one('img')['src']
            soup = self.get_soup(self.BASE_URL + result['href'])

            seasons = soup.select('div.temporada-container h4 a')
            for season in seasons:
                if season['href'].find('none') == -1:
                    self.submit_search_result(
                        link_url = self.BASE_URL + season['href'],
                        link_title = season.text,
                        image = image
                    )

    def parse(self, parse_url, **extra):
        self.id = parse_url.split('/capitulo/')[1].split('/')[0]
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)


    def _parse_parse_page(self, soup):
        title = soup.select_one('h3').text.strip()
        season, episode = self.util.extract_season_episode(title)
        soup1 = self.get_soup(self.BASE_URL + '/caps?id=' + self.id)

        for link in soup1.select('a.thelink'):
            self.submit_parse_result(
                index_page_title = self.util.get_page_title(soup),
                link_url=link['href'],
                link_title=title,
                series_season=season,
                series_episode=episode
            )
