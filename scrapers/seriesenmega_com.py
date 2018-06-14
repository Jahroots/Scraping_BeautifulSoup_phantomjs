# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SeriesEnMega(SimpleScraperBase):
    BASE_URL = 'http://seriesenmega.com'

    def setup(self):
        raise NotImplementedError('Deprecated, website just shows ads.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Sorry, but nothing matched your search criteria.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('h2.post-box-title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1 span[itemprop="name"]').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('p a'):
            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url=link['href'],
                link_title= link.text,
                series_season=season,
                series_episode=episode
            )

    def get(self, url, **kwargs):
        return super(SeriesEnMega, self).get(url, allowed_errors_codes=[404], **kwargs)
