# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Tuserie(SimpleScraperBase):
    BASE_URL = 'http://tuserie.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'No found.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('article div.boton a[class="button active"]')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = (soup.select_one('h1.title-post') or soup.select_one('.post-main h2')).text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.post p strong a'):
            try:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link['href'],
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )
            except Exception as e:
                self.log.error(link)
                # self.show_in_browser(soup)
                raise e
