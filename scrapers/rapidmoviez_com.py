# -*- coding: utf-8 -*-
import time

from sandcrawler.scraper import CloudFlareDDOSProtectionMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.extras import FlashVarsMixin


class RapidMoviez(CloudFlareDDOSProtectionMixin, FlashVarsMixin, SimpleScraperBase):
    BASE_URL = 'http://rmz.cr'

    OTHER_URLS = ['http://rapidmoviez.com', ]



    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/%s/releases' % self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return 'No movies/tv show available.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>')
        self.log.debug('-' * 30)
        # link = soup.find('a', text='More Releases...')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):

        for result in soup.select('.title'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):
        self.soup2parse = soup
        title = (soup.find('a', itemprop='name') or soup.select_one('.blogs h2')).text.strip()
        season, episode = self.util.extract_season_episode(title)

        for block in soup.select('pre.links'):
            for link in self.util.find_urls_in_text(block.text):
                if link.startswith('http'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link.strip(),
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )

        for link in soup.select('.blogs a') + soup.select('.links a'):
            if link.get('href') and link['href'].startswith('http') \
                    and 'imdb.com/' not in link['href'] and '.png' not in link['href'] \
                    and link.get('style', '') != 'text-decoration: line-through;':
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link['href'],
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )
        # # lot of magic below :-\
        # dl = soup.find('div', {'class': 'fullsize'}, text='Download').parent
        # links = [lnk for lnk in self.util.find_urls_in_text(dl.text) if 'imdb.com/' not in lnk and '.png' not in lnk]
        # links2 = []
        # for link in links:
        #     pos = link.find('http', 2)
        #     if pos > 0:
        #         links2.extend([link[:pos], link[pos:]])
        #     else:
        #         links2.append(link)
        #
        #
        # # from pprint import pprint
        # # pprint(links2)
        # for link in links2:
        #     if link.endswith('Uploaded.net:'):
        #         link=link[:-13]
        #     elif link.endswith('upload:'):
        #         link = link[:-7]
        #
        #     print link
        #     if not soup.find('a', href=link, style='text-decoration: line-through;'):
        #         self.submit_parse_result(
        #             link_url=link,
        #             link_title=title,
        #             series_season=season,
        #             series_episode=episode
        #         )

        # CLICK TO SEE THE LINKS
        div = soup.find_all('div', dict(klass='.ppu2h', style="display:none"))
        if div:
            for link in self.util.find_urls_in_text(div.text):
                self.submit_parse_result(
                                         link_url=link['href'],
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode
                                         )
