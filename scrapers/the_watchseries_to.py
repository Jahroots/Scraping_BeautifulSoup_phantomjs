# -*- coding: utf-8 -*-
import base64

from sandcrawler.scraper import SimpleScraperBase


class TheWatchseries_to(SimpleScraperBase):
    BASE_URL = 'http://dwatchseries.to'
    OTHER_URLS = ['http://itswatchseries.to', 'http://www.tvbuzer.com', 'http://onwatchseries.to', 'http://watchseriesonline.in', 'http://watchseriesonline.eu',
                  'http://xwatchseries.to']

    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        raise NotImplementedError('Duplicate scraper - use the_watch_series.py')
        self.register_scraper_type(SimpleScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(SimpleScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(SimpleScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(SimpleScraperBase.URL_TYPE_LISTING, url)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/{}'.format(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next Page')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _fetch_no_results_text(self):
        return 'Sorry we do not have any results for that search'

    def _parse_search_result_page(self, soup):
        results = soup.select('div[class*="search-item"] div[valign="top"] a[title]')
        for result in results:
            link = result
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.channel-title')
        if title:
            title = title.text[5:-8].strip()

        for epis_link in soup.select('.listings.show-listings a'):
            epis_soup = self.get_soup(epis_link['href'])

            sea, episode = self.util.extract_season_episode(title)
            for a in epis_soup.select('#myTable a.buttonlink'):
                if 'Sponsored' in a['title']:
                    continue
                if '/cale.html' in a['href']:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=base64.b64decode(
                                                 a['href'][a['href'].find("cale.html?r=") + 12:]),
                                             link_title=title,
                                             series_season=sea,
                                             series_episode=episode
                                             )
                else:
                    dload_soup = self.get_soup(a['href'])

                    link = dload_soup.select_one('.myButton')['href']
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link,
                                             link_title=title,
                                             series_season=sea,
                                             series_episode=episode
                                             )
