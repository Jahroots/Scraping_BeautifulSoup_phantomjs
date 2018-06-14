# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase


class MegaSearchCo(ScraperBase):
    BASE_URL = 'http://megasearch.co'
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _do_search(self, search_term, page=1):
        return self.post_soup(
            self.BASE_URL + '/search',
            data={
                'q': search_term,
                'p': page,
                'h': 0,
                'c': 0,
                's': 2,  # Sort by most recent
                'a': '',
                'm1': '',
                'm2': '',
            },
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )

    @staticmethod
    def _has_result(soup):
        return bool(soup.select('a.link_result'))

    def search(self, search_term, media_type, **extra):
        page = self._do_search(search_term)
        if not self._has_result(page):
            return self.submit_search_no_results()
        self._parse_search_page(page)

        page_no = 1
        while self._has_result(page) and self.can_fetch_next():
            page_no += 1
            page = self._do_search(search_term, page=page_no)
            self._parse_search_page(page)

    def _parse_search_page(self, soup):
        for result in soup.select('a.link_result'):
            title = result.find('span', 'title').text.strip()
            self.submit_search_result(
                link_url=result['href'],
                link_title=title,
            )

    def parse(self, parse_url, **kwargs):
        for content in self.get_each([parse_url, ]):
            for obfuscated in re.findall(
                    "document.write\(decodeURIComponent\('([^']*)'\)\)", content):
                soup = self.make_soup(self.util.unquote(obfuscated))

                for link in soup.select('a'):
                    # Follow it, with referer included.
                    resp = self.get(
                        link['href'],
                        headers={
                            'Referer': parse_url,
                        })
                    # then submit that.
                    self.submit_parse_result(index_page_title=soup.title.text.strip() if soup.title else '',
                                             link_url=resp.url
                                             )
