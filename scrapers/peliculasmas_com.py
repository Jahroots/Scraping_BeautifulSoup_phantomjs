# -*- coding: utf-8 -*-
import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Peliculasmas(SimpleScraperBase):
    BASE_URL = 'http://peliculasmas.com'
    OTHER_URLS = ['http://www.peliculasmas.com', ]

    def setup(self):
        raise NotImplementedError('Deprecated, Duplicate of RepelisTV')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        # self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):
        return super(Peliculasmas, self).get(url, **kwargs)

    def _fetch_no_results_text(self):
        return 'Sorry, we couldn\'t find any results based on your search query.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='» Siguiente')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('.search-results .entry-title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.find('a', rel="bookmark").text.strip()

        for iframe in soup.find_all('iframe', dict(id="movieframe")):
            if iframe['src'].startswith('http') and '/mirror/' not in iframe['src']:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=iframe['src'],
                                         link_title=title,
                                         # series_season=sea,
                                         # series_episode=episode
                                         )

        for a in [aa for aa in soup.find_all('a') if '/mirror/' in aa.get('href', '')]:
            # time.sleep(5)
            soup404 = self.get_soup(
                a.get('href'),
                allowed_errors_codes=[404],
            )

            form_inp = soup404.select('#wp-mirror-dd-form input')
            if not form_inp:
                continue
            data = {}
            for input in form_inp:
                data[input['name']] = input['value']
            time.sleep(6)
            suup = self.post_soup(
                a.get('href'),
                data=data,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:43.0) Gecko/20100101 Firefox/43.0',
                }
            )

            for link in suup.find('a', {'target': "_blank"}):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=str(link),
                                         link_title=title,
                                         # series_season=sea,
                                         # series_episode=episode
                                         )
