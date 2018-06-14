# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class IdoWatch(SimpleScraperBase):
    BASE_URL = 'http://idowatch.net'

    def setup(self):

        raise NotImplementedError('Deprecated - now an OSP with no search.')

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        self._login()
        return self.BASE_URL + '/?op=search&k={}&user=&tag=&cat_id='.format(search_term)

    def _fetch_no_results_text(self):
        return 'Apologies, but no results were found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next →')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _login(self):
        self.post(self.BASE_URL, data=dict(op='login', redirect='', login='sands', password='sands8'))

    def _parse_search_result_page(self, soup):
        all_results = soup.select('a.title')
        if not all_results:
            self.submit_search_no_results()

        for result in all_results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.title.text.replace('Watch ', '').strip()
        season, episode = self.util.extract_season_episode(title)

        html = str(soup)
        if '.mp4' in html:
            url = html.split('.mp4')[0].split(' "')[-1]+'.mp4'
            self.submit_parse_result(
                link_url=url,
                link_title=title,
                series_season=season,
                series_episode=episode
            )
