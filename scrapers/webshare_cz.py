# -*- coding: utf-8 -*-

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.exceptions import ScraperParseException

class Webshare(ScraperBase):
    BASE_URL = 'https://en.webshare.cz'
    OTHER_URLS = []
    LONG_SEARCH_RESULT_KEYWORD = '2015'



    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _do_search(self, search_term, offset=0,):
        return self.post_soup(
            self.BASE_URL + '/api/search/',
            data={
                'what': search_term,
                'category': 'video',
                'sort': 'rating',
                'offset':offset,
                'limit':25,
                'wst': '',
            },
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

    @staticmethod
    def _get_total_pages(total_items=0, items_per_page = 25):

        number_of_pages = ( total_items + items_per_page - 1) // items_per_page
        return number_of_pages

    @staticmethod
    def _get_total_records(soup):
        total = 0
        if soup.total:
            total = int(soup.total.string)
        return total

    @staticmethod
    def _has_result(soup):
        total = 0
        if soup.total:
            total = int(soup.total.string)

        return total>0

    @staticmethod
    def _has_media_link(soup):
        if soup.link:
            return True
        else:
            return False

    @staticmethod
    def _parse_media_link(soup):
        if soup.link:
            return soup.link.text.strip()


    def search(self, search_term, media_type, **extra):
        self.get(url=self.BASE_URL + '/#/search')
        soup = self._do_search(search_term)
        if not self._has_result(soup):
            return self.submit_search_no_results()

        total_records = self._get_total_records(soup)
        self.log.info('Total no. of records %s' % total_records)
        page_no = 1
        offset = 0
        total_pages = self._get_total_pages(total_records)
        while True:
            if self._has_result(soup):
                self._parse_search_page(soup)
            page_no += 1
            offset += 25
            if page_no <= total_pages and self.can_fetch_next():
                soup = self._do_search(search_term, offset=offset)
            else:
                break

    def _parse_search_page(self, soup):

        for result in soup.find_all('file'):
            if result.find('ident'):
                ident = result.find('ident').text.strip()
            if result.find('name'):
                title = result.find('name').text.strip()
            if result.find('stripe'):
                image = result.find('stripe').text.strip()
                m = re.search(r'(^.+?\-)M.jpg',image)
                if m:
                    image = m.group(1) + 'S.jpg'

            self.submit_search_result(
                ##https://en.webshare.cz/#/file/2ik5rT1Jv2/300-vzestup-rise-avi
                link_url=self.BASE_URL + '/#/file/' + ident,
                link_title=title,
                image=self.BASE_URL + image,
            )

    def _get_media_link(self, ident):
        return self.post(
            # https://en.webshare.cz/api/file_info/
            #https://en.webshare.cz/api/file_link/
            self.BASE_URL + '/api/file_link/',
            data={
                'ident': ident,
                'password': '',
                'wst': '',
            },
            headers={'X-Requested-With': 'XMLHttpRequest','Referer':self.BASE_URL}
        )

    def _get_media_info(self, ident):
        return self.post_soup(
            # https://en.webshare.cz/api/file_info/
            self.BASE_URL + '/api/file_info/',
            data={
                'ident': ident,
                'password': '',
                'wst': '',
            },
            headers={'X-Requested-With': 'XMLHttpRequest','Referer':self.BASE_URL}
        )


    def parse(self, parse_url, **kwargs):

        for content in self.get_each([parse_url, ]):
            ##https://en.webshare.cz/#/file/2ik5rT1Jv2/300-vzestup-rise-avi
            m = re.search(r'file\/(\w+)?[\/]?',parse_url)
            ident = ''
            if m:
                ident = m.group(1)
            index_page_title = ''
            link_title = ''
            link_url = ''
            page_soup = self.make_soup(content=content)
            index_page_title = self.util.get_page_title(page_soup)
            soup = self._get_media_info(ident)
            if soup.name:
                link_title = soup.find('name').text
            season, episode = self.util.extract_season_episode(link_title)
            soup = self._get_media_link(ident)
            text = soup.content
            if "<link>" in text:
                m = re.search(r'<link>(.+)?<\/link>', text)
                if m:
                    link_url = m.group(1)

            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=link_url,
                                     link_title=link_title,
                                     series_season=season,
                                     series_episode=episode)


