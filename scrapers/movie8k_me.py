# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Movie8K(SimpleScraperBase):
    BASE_URL = 'https://www.movie9k.to/'
    OTHER_URLS = ['http://www.movie8k.me','http://www.movie8k.tw' ]
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        raise NotImplementedError('Website no longer available')

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(self.BASE_URL + '/search', data=dict(searchquery=search_term)))

    def _fetch_no_results_text(self):
        return 'Sorry, your search'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='››')
        self.log.debug('------------------------')
        return self.BASE_URL + '/' + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('#tablemoviesindex #tdmovies a')
        if not results:
            self.submit_search_no_results()

        for link in results:
            if link.parent['width'] == '550':
                self.submit_search_result(
                    link_url=link['href'],
                    link_title=link.text)

    def _parse_parse_page(self, soup, find_mirrors=True):
        title = soup.select_one('#maincontent5 h1').text.strip()
        series_season, series_episode = self.util.extract_season_episode(title)
        try:
            link = soup.find('div', style="width:742px")
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.find_all('a')[-1]['href'],
                                     link_text=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )
        except AttributeError:
            pass

        # mirrors
        if find_mirrors:
            for mirr in soup.select("#tablemoviesindex2 td a"):
                if mirr.parent['width'] == "150":
                    self._parse_parse_page(self.get_soup(mirr['href']), find_mirrors=False)
