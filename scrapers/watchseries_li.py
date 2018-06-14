# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Watchseries_li(SimpleScraperBase):
    BASE_URL = 'http://watchseries.sk'
    OTHERS_URLS = ['http://watch-series.is', 'http://watchseries.do', 'http://www.watchseries.li', 'http://watchseries.cr/', 'http://watchseries.lt']
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search?s=' + search_term

    def _fetch_no_results_text(self):
        return 'is not found in our database'

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('a[class="videoHname title"]')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            soup = self.get_soup(result['href'])

            items = soup.select('a.videoHname')

            for item in items:
                if item:
                    self.submit_search_result(
                        link_url = item['href'],
                        link_title = item.text
                    )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        season, episode = self.util.extract_season_episode(title)

        for epis_link in soup.select('td.view_link a'):
            epis_soup = self.get_soup(epis_link['href'])
            link = ''
            if epis_soup.select_one('div.wrap a'):
                link = epis_soup.select_one('div.wrap a')['href']

                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url = link,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )


class Watchseries_lt(Watchseries_li):
    BASE_URL = 'http://watchseries.do'
    OTHER_URLS = ['http://watchseries.lt', 'http://watchseries.cr']

    def setup(self):
        raise NotImplementedError('Deprecated duplicate of Watchseries_li')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search?s=' + search_term

    def _fetch_no_results_text(self):
        return 'Found 0 matches'

    def _parse_search_result_page(self, soup):
        results = soup.select('a.videoHname.title')
        if not results:
            self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.page-title > h1').text[5:].strip()

        for epis_link in soup.select('.videoHname'):
            epis_soup = self.get_soup(epis_link['href'])

            sea, episode = self.util.extract_season_episode(epis_soup.select_one('.page-title > h1').text)

            for a in epis_soup.select('.wpb_button.wpb_btn-primary.wpb_btn-small.watchthislink'):
                if a['href'].startswith('http'):
                    dload_soup = self.get_soup(a['href'])

                    link = dload_soup.select_one('.wpb_button.wpb_btn-primary.wpb_regularsize').parent['href']
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link,
                                             link_title=title,
                                             series_season=sea,
                                             series_episode=episode
                                             )
