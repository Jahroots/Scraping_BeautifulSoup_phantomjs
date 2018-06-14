# -*- coding: utf-8 -*-
import json

from sandcrawler.scraper import ScraperBase


class Streamay(ScraperBase):
    BASE_URL = 'http://streamay.la'
    OTHER_URLS = ['http://streamay.ws', 'https://streamay.bz', 'http://streamay.com', ]
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(self.BASE_URL + '/search',
                           data=dict(k=search_term),
                           headers={'X-Requested-With': 'XMLHttpRequest'})
        )

    def _parse_search_results(self, soup):
        results = json.loads(soup.p.text)
        if 'empty' in results:
            self.submit_search_no_results()
            return
        # from pprint import pprint;        pprint(results)
        for result in results:
            result = result['result']
            self.submit_search_result(link_url=result['url'],
                                      link_title=result['originalTitle'])

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        f_title = soup.select_one('.titlo')
        if f_title:
            film_title = f_title.text.replace('streaming', '').strip()
            if ' - Saison ' in film_title:  # self.mediatype == ScraperBase.MEDIA_TYPE_TV:
                season = film_title[film_title.find(' - Saison ') + 10:]

                for epis in soup.select('.btns a'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=epis['href'],
                                             link_title=film_title,
                                             series_season=season,
                                             series_episode=epis.text)
            else:  # film
                for host in soup.select('.lecteurs.nop li a'):
                    url = json.loads(
                        self.get(
                            self.BASE_URL + '/streamer/{}/{}'.format(host.attrs['data-id'],
                                                                     host.attrs['data-streamer'])).content
                    )['code']

                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url='http:' + url if url.startswith('//') else url,
                                             link_title=film_title,
                                             )

                for frame in soup.find_all('iframe', allowfullscreen="true"):
                    link = frame['src']
                    link = 'http:' + link if link.startswith('//') else link
                    # link = self.get(link).url if link.startswith('http://streamay.com/netu.php') else link

                    self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=link,
                                             link_title=film_title,
                                             )

                    # for serie in soup.findAll('a', target='seriePlayer'):
                    # for serie in soup.findAll('a', rel="zoombox"):
                    #     self.submit_parse_result(link_url=serie['href'],
                    #                              link_title=0,
                    #                              series_season=0,
                    #                              series_episode=0
                    #                              )
