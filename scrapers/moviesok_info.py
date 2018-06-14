# -*- coding: utf-8 -*-
from requests import head

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Moviesok(SimpleScraperBase):
    BASE_URL = 'http://moviesok.info'
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


    def _fetch_search_url(self, search_term, media_type=None, page=0):
        self.start = page
        self.search_term = search_term
        return '{base_url}/search/index.xhtml?keyword={search_term}&n={page}'.format(base_url=self.BASE_URL,
                                                                                     search_term=search_term,
                                                                                     page=page)



    def _fetch_no_results_text(self):
        return u'sorry the results you need not found'


    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup.text).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, page=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for result in soup.select('.media-heading a'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.active').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.table.table-bordered a'):
            href = self.get_redirect_location(self.BASE_URL + link['href'])
            if href:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=href,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )


if __name__ == '__main__':
    # development / debug mode
    import logging as log
    from pprint import pprint as pp

    log.basicConfig(level=log.DEBUG, format='%(levelname)s %(message)s')

    scr = Moviesok()
    scr.setup()
    pp(scr.search('super', ScraperBase.MEDIA_TYPE_FILM))
