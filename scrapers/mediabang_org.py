# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class MediaBang(SimpleScraperBase):
    BASE_URL = 'http://mediabang.org'

    def setup(self):

        raise NotImplementedError('Site unavailable.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        if media_type == ScraperBase.MEDIA_TYPE_TV:
            return self.BASE_URL + "/tv/?q=" + self.util.quote(search_term)
        elif media_type == ScraperBase.MEDIA_TYPE_FILM:
            return self.BASE_URL + "/?q=" + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return "Sorry, we can't find the content you're looking for."

    def _fetch_next_button(self, soup):
        curr = soup.select_one('.current')
        if curr:
            nxt = curr.next_sibling
            if nxt.name == 'li':
                self.log.debug('------------------------')
                return self.BASE_URL + nxt.a['href']

    def _parse_search_result_page(self, soup):
        all_results = soup.select('.product__ttl a')
        if not all_results:
            self.submit_search_no_results()

        for result in all_results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup, serie_mode=False):

        series = soup.select('.accordion__list li a')
        if series:
            for ser in series:
                self._parse_parse_page(self.get_soup(self.BASE_URL + '/' + ser.href),
                                       serie_mode=True)

        for link in soup.select('.link__ttl span.ext-link'):
            soup2 = self.get_soup(self.BASE_URL + link['data-href'])
            url = soup2.select_one('iframe')['src']
            title = soup.select_one('.product__ttl').text.replace('\t\t', ' ').replace('\n', '').replace('  ',
                                                                                                         ' ').strip()
            season, episode = self.util.extract_season_episode(title)
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=url,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )
