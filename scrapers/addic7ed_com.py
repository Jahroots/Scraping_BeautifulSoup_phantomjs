# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Addic7ed(SimpleScraperBase):
    BASE_URL = 'http://www.addic7ed.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        raise NotImplementedError('site provides subtitleas and/or translations only')

        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        self.media_type = media_type
        return self.BASE_URL + '/search.php?search={}&Submit=Search'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return 'Sorry, your search'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.tabel a'):
            rslt_type = result.parent.parent.td.img['src'].endswith('film.png')
            if (rslt_type and self.media_type == self.MEDIA_TYPE_FILM) or (
                not rslt_type and self.media_type == self.MEDIA_TYPE_TV):
                self.submit_search_result(
                    link_url=self.BASE_URL +'/'+result['href'],
                    link_title=result.text
                )

    def _parse_parse_page(self, soup):
        dload_page_url = soup.find('a', text='Multi Download')
        if not dload_page_url:
            return

        title = soup.select_one('.titulo').text
        title = (title[:-8] if title.endswith('subtitles') else title).strip()
        season, episode = self.util.extract_season_episode(title)

        dl_soup = self.get_soup(self.BASE_URL+dload_page_url['href'])

        for src in soup.select('.section iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url='http:' + src['src'] if src['src'].startswith('//') else src['src'],
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode
                                     )