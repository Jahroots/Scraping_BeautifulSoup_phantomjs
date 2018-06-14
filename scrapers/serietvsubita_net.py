# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SerieTVsubita(SimpleScraperBase):
    BASE_URL = 'http://serietvsubita.net'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'ita'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Sorry, but you are looking for something that isn\'t here'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.p-cont h2 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.p-cont h2').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.entry p a')[1:-1]:

            href = link['href']
            if href.startswith('http://ncrypt.in/'):
                href = self.get_redirect_location(href.replace("link-", "frame-"))

            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=href,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )
