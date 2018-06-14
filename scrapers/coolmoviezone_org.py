# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class CoolMovieZone(SimpleScraperBase):
    BASE_URL = 'http://coolmoviezone.info'
    OTHER_URLS = ['http://coolmoviezone.net', 'http://coolmoviezone.org']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return 'You are possible misspelled'

    def _fetch_no_results_pattern(self):
        return 'You\s*are\s*possible\s*misspelled'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next Page »')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('.postarea h1 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('.postarea h1').text.strip()
        season, episode = self.util.extract_season_episode(title)
        urls = {}

        for link in soup.select('a[href*="rd.html?url="]'):
            urls[link.href[37:]] = link.text

        if urls:
            for key in urls:
                self.submit_parse_result(
                    index_page_title=soup.title.text.strip(),
                    link_url=key,
                    link_title=urls[key],
                    series_season=season,
                    series_episode=episode
                )
        for link in soup.select('table.source-links a'):
            if self.BASE_URL in link.href:
                continue
            self.submit_parse_result(
                index_page_title=soup.title.text.strip(),
                link_url=link.href,
                link_title=link.text,
                series_season=season,
                series_episode=episode
            )
