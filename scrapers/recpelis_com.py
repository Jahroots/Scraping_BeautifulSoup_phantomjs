# -*- coding: utf-8 -*-

import base64
import re
import json
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Recpelis(SimpleScraperBase):
    BASE_URL = 'https://repelis.tv'
    OTHERS_URLS = ['http://www.recpelis.com', 'http://www.repelis.tv']
    SINGLE_RESULTS_PAGE = True

    def _get_sucuri_cookie(self, html):
        if 'sucuri_cloudproxy_js' in html:
            match = re.search("S\s*=\s*'([^']+)", html)
            if match:
                s = base64.b64decode(match.group(1))
                s = s.replace(' ', '')
                s = re.sub('String\.fromCharCode\(([^)]+)\)', r'chr(\1)', s)
                s = re.sub('\.slice\((\d+),(\d+)\)', r'[\1:\2]', s)
                s = re.sub('\.charAt\(([^)]+)\)', r'[\1]', s)
                s = re.sub('\.substr\((\d+),(\d+)\)', r'[\1:\1+\2]', s)
                s = re.sub(';location.reload\(\);', '', s)
                s = re.sub(r'\n', '', s)
                s = re.sub(r'document\.cookie', 'cookie', s)
                try:
                    cookie = ''
                    exec (s)
                    match = re.match('([^=]+)=(.*)', cookie)
                    if match:
                        return {match.group(1): match.group(2)}
                except Exception as e:
                    self.log.warning('Exception during sucuri js: %s' % e)

        return {}

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        # self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/buscar/?s={}'.format(search_term)


    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next= soup.select_one('div.pagenavi a.last')
        if next:
            return next['href']
        return None

    def _parse_search_results(self, soup):

        results = soup.select('ul[class="search-results-content infinite"] a[class="info-title one-line"]')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for link in results:

            self.submit_search_result(
                link_url=link.href,
                link_title=link.select_one('h2').text)


        next = self._fetch_next_button(soup)
        if next and self.can_fetch_next():
            soup = self.get_soup(next)
            self._parse_search_results(soup)



    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1').text
        links = soup.select('iframe[data-src]')
        for link in links:

            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=link['data-src'],
                                     link_title= title)

        links = soup.select('table a[href*="iframe"]')
        for link in links:
            soup = self.get_soup(link.href)
            iframe = soup.select_one('iframe')
            if iframe:
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=iframe['src'],
                                         link_title=title)

        return

        # def search(self, search_term, media_type, **extra):
        #     # curl
        #     # 'http://www.recpelis.com/?s=super' - H
        #     # 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' - H
        #     # 'Accept-Encoding: gzip, deflate' - H
        #     # 'Accept-Language: en-GB,en;q=0.5' - H
        #     # 'Connection: keep-alive' - H
        #     # 'Cookie: sucuri_cloudproxy_uuid_7c33ba3c6=8c8b7ae31034dd6434d38d5b213ccf19; PHPSESSID=h0pdkf4a1ac70dt1ealvg2kg22; haha_unique_user=1' - H
        #     # 'Host: www.recpelis.com' - H
        #     # 'Referer: http://www.recpelis.com/?s=esfkbswkfwsjkef' - H
        #     dt = self.http_session().get(self.BASE_URL, headers={
        #         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:42.0) Gecko/20100101 Firefox/42.0'
        #     })
        #     self.coo = self._get_sucuri_cookie(dt._content)
        #
        #     resp = self.http_session().get(self._fetch_search_url(search_term, media_type),
        #                                    headers={'Cookie': '{}; haha_unique_user=1'.format(
        #                                        ';'.join('%s=%s' % (k, v) for k, v in self.coo.items())),
        #                                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:42.0) Gecko/20100101 Firefox/42.0'})
        #     self._parse_search_results(self.make_soup(unicode(resp.content, 'utf8'),
        #                                               url=self._fetch_search_url(search_term, media_type)))



            # self._parse_search_result_page(soup)
        #
        # next_button_link = self._fetch_next_button(soup)
        # if next_button_link and self.can_fetch_next():
        #     self._parse_search_results(
        #         self.make_soup(
        #             self.http_session().get(next_button_link,
        #                                     headers={'Cookie': '{}; haha_unique_user=1'.format(
        #                                         ';'.join('%s=%s' % (k, v) for k, v in self.coo.items())),
        #                                         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:42.0) Gecko/20100101 Firefox/42.0'}
        #                                     ).content)
        #     )


        # def _fetch_next_button(self, soup):
        #     link = soup.find('a', text='»')
        #     self.log.debug('------------------------')
        #     return link['href'] if link else None

        # def _parse_search_result_page(self, soup):
        #     for link in soup.select('.list_f a.poster'):
        #         self.submit_search_result(
        #             link_url=link['href'],
        #             link_title=link.title)

        # def parse(self, parse_url, **extra):
        #     if 'coo' not in self.__dict__:
        #         dt = self.http_session().get(self.BASE_URL, headers={
        #             'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:42.0) Gecko/20100101 Firefox/42.0'
        #         })
        #         self.coo = self._get_sucuri_cookie(dt._content)
        #
        #     soup = self.make_soup(
        #         self.http_session().get(parse_url,
        #                                 headers={'Cookie': '{}; haha_unique_user=1'.format(
        #                                     ';'.join('%s=%s' % (k, v) for k, v in self.coo.items())),
        #                                     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:42.0) Gecko/20100101 Firefox/42.0'}
        #                                 ).content)
        #     self._parse_parse_page(soup)


        # series

        # if soup.select_one('.episode-guide-header'):
        #     for ser_link in soup.select('.episode-title.col-xs-7.pad0 a'):
        #         ser_soup = self.make_soup(
        #             self.http_session().get(ser_link['href'],
        #                                     headers={'Cookie': '{}; haha_unique_user=1'.format(
        #                                         ';'.join('%s=%s' % (k, v) for k, v in self.coo.items())),
        #                                         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:42.0) Gecko/20100101 Firefox/42.0'}
        #                                     ).content)
        #         self._parse_parse_page(ser_soup)
        #
        # else:
        #     title = soup.select('.container-fluid h1')[1].text.strip()
        #     series_season, series_episode = self.util.extract_season_episode(title)  # .replace(',', ''))
        #
        #     for link in soup.select('.btn.btn-xs.btn-info a'):
        #         self.submit_parse_result(index_page_title=soup.title.text.strip(),
        #                                  link_url='http:' + link['href'] if link['href'].startswith('//') else link['href'],
        #                                  link_text=title,
        #                                  series_season=series_season,
        #                                  series_episode=series_episode,
        #                                  )
        #
        #     for frame in soup.select('.tab-content iframe'):
        #         self.submit_parse_result(index_page_title=soup.title.text.strip(),
        #                                  link_url='http:' + frame['src'] if frame['src'].startswith('//') else frame['src'],
        #                                  link_text=title,
        #                                  series_season=series_season,
        #                                  series_episode=series_episode,
        #                                  )
