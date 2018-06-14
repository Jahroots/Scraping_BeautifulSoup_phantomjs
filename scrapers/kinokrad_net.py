# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import UppodDecoderMixin
from sandcrawler.scraper import OpenSearchMixin
import re

class Kinokrad(OpenSearchMixin, SimpleScraperBase, UppodDecoderMixin):
    BASE_URL = 'http://kinokrad.co'

    SINGLE_RESULTS_PAGE = True

    UPPOD_HASH1 = ["v", "2", "U", "V", "N", "5", "R", "w", "p", "y", "T", "X", "z", "Q", "x", "8", "s", "f", "g", "i", "c", "t", "m", "3", "n", "="]
    UPPOD_HASH2 = ["u", "Y", "0", "6", "B", "l", "G", "H", "D", "e", "L", "J", "9", "I", "d", "a", "1", "Z", "b", "M", "7", "o", "4", "W", "k", "P"]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    
    def _parse_search_result_page(self, soup):
        for result in soup.select('.searchitem h3 a'):
            if not result.img:
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result.text
                )

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)

        title = soup.select_one('#dle-content h1')
        season, episode = None, None
        if title:
            title = title.text.strip()
            season, episode = self.util.extract_season_episode(title)


        # Dig out filmSsourceF - the flash film source
        for script in soup.find_all('script'):
            srch = re.search('var filmSourceF = "(.*?)"', script.text)
            if srch:
                filmSourceF = srch.group(1)

                decoded = self.decode(
                    filmSourceF,
                    self.UPPOD_HASH1,
                    self.UPPOD_HASH2
                )
                if decoded.startswith('http'):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=decoded,
                        series_season=season,
                        series_episode=episode
                    )
                else:
                    self.log.error('Got bad decoded response=%s from uppod decode of %s',
                        decoded, filmSourceF)


        for src in soup.select('.dle-content iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url='http:' + src['src'] if src['src'].startswith('//') else src['src'],
                series_season=season,
                series_episode=episode
                )

        for src in soup.select('.section #tuber object param'):
            if src.get('name') == 'movie':
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=src['value'],
                    series_season=season,
                    series_episode=episode
                    )

        # serial
        if soup.find('select', {'name': 'select_items'}):
            for serial_link in soup.find('select', {'name': 'select_items'}).findAll('option'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=serial_link['value'],
                    link_title=serial_link.text,
                    series_season=season,
                    series_episode=episode
                    )

        # serial
        if soup.select_one('#uber-vk-write'):
            for link in self.util.find_urls_in_text(unicode(soup.select_one('#uber-vk-write'))):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=title,
                    series_season=season,
                    series_episode=episode
                    )

        for iframe in re.findall('<iframe .*?><\/iframe>', unicode(soup)):
            iframe_soup = self.make_soup(iframe)
            iframe_element = iframe_soup.select_one('iframe')
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe_element['src'],
                link_title=title,
                series_season=season,
                series_episode=episode
            )
