# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Wkinie(SimpleScraperBase):
    BASE_URL = 'http://wkinie.tv'

    # OTHER_URLS = ['http://tom51.com']
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ]:  # + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        raise NotImplementedError('Website No Longer required.')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/searchFile,{}.html'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Nie ma strony o ID'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='»')
        self.log.debug('---------------')
        return next['href'] if next else None

    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('.grid center a b'):
            self.submit_search_result(link_url=link.parent.href,
                                      link_title=link.text
                                      )
            found = True
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):

        title = soup.title.text[-21:]
        series_season, series_episode = self.util.extract_season_episode(title)

        for iframe in soup.find_all('iframe', width='500'):
            src = iframe.get('src', iframe.get('data-src', None))
            if src:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=src,
                                         link_title=title,
                                         series_season=series_season, series_episode=series_episode
                                         )
