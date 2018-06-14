# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SuperEstrenoCom(SimpleScraperBase):
    BASE_URL = 'http://www.estrenosx.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Siguientes')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class*="tumbail post"] a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('#content h1').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('a.online'):
            self.log.debug(link)
            text = link.text

            if link['href'].split('cid') and len(link['href'].split('cid')) > 1:
                link = link['href'].split('cid=')[1]
            else:
                link = link['href']

            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link,
                link_title=text,
                series_season=season,
                series_episode=episode
            )
