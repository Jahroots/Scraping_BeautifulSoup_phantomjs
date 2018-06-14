# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class OstFilmTv(SimpleScraperBase):
    BASE_URL = 'http://ostfilm.org'
    OTHER_URLS = ['http://ostfilmtv.org', 'http://ostfilm.org']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('h2.post-title a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2.post-title').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('p iframe'):
            href = link['src']
            if href.find('http') == -1:
                href = 'http:' + href

            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url= href,
                link_title=title,
                series_season=season,
                series_episode=episode
            )
