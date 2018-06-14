# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable
import json

class SeriesYonkisSx(SimpleScraperBase):
    BASE_URL = 'https://yonkis.to'
    OTHER_URLS = ['http://seriesyonkis.sx', 'http://www.seriesyonkis.sx']
    USER_AGENT_MOBILE = False


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.long_parse = True


    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)



    def _fetch_no_results_text(self):
        return u'Sin resultados'

    def _parse_search_results(self, soup):

        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)

        links = soup.select_one('.paginator')
        if links:
            link = links.find('a', text='>')
            if link and self.can_fetch_next():
                next_soup = self.post_soup(
                    self.BASE_URL + '/buscar/serie',
                    headers={'Origin': 'https://yonkis.to', 'Cache-Control': 'max-age=0',
                             'Content-Type': 'application/x-www-form-urlencoded'},
                    data=dict(keyword=self.search_term, search_type='serie')
                )

                self._parse_search_results(next_soup)

    def search(self, search_term, media_type, **extra):
        self.search_term = search_term
        soup = self.post_soup(self.BASE_URL + '/buscar/serie',
                              data=dict(keyword=search_term, search_type='serie'), headers = {'Origin': 'https://yonkis.to', 'Cache-Control': 'max-age=0',
                                                                                              'Content-Type' : 'application/x-www-form-urlencoded'})

        self._parse_search_results(soup)

    def _parse_search_result_page(self, soup):
        for result in soup.select('ul.results li h2 a'):
            self.submit_search_result(link_url=self.BASE_URL + result['href'])



    def _parse_parse_page(self, soup):
        for season in soup.select('.expand'):

            for episode in season.findChildren('a'):
                dload_locations = self.get_soup(self.BASE_URL + episode['href'])
                series_season, series_episode = episode.strong.text.strip().split('x')

                for loc in dload_locations.select('.episode-server'):
                    link_url, link_title = self._parse_out_page(
                        self.BASE_URL + loc.a['href'])
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link_url,
                                             link_title=link_title,
                                             series_season=series_season,
                                             series_episode=series_episode
                                             )

    @cacheable()
    def _parse_out_page(self, url):
        loc_soup = self.get_soup(url)
        if 'No input file specified' not in loc_soup.text:
            link = loc_soup.select_one('a.link.p2')
            link = link['href']
            return (
                link.encode('utf-8'),
                loc_soup.select_one('h2.header-subtitle.full-width.go-subtitle').text.encode('utf-8'),
            )
        else:
            return (None, None)

