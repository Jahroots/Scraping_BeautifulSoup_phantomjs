# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class MovieRulzTo(SimpleScraperBase):
    BASE_URL = 'https://movierulz.pe'
    OTHER_URLS = [
        'http://www.movierulz.gs'
        'https://www.movierulz.tw',
        'http://www.movierulz.at',
        'http://www.movierulz.nz',
        'http://www.movierulz.gr',
        'http://www.movierulz.sx',
        'http://www.movierulz.so',
        'http://www.movierulz.ms',
        'http://www.movierulz.mg',
        'http://www.movierulz.mx',
        'http://www.movierulz.cm',
        'http://www.movierulz.cx',
        'http://www.movierulz.ch',
        'http://www.movierulz.mn'
    ]

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"
        self._request_connect_timeout = 300
        self._request_response_timeout = 600

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def _fetch_no_results_text(self):
        return 'This might because it no longer exists or we have moved it'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='&larr; Older Entries')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.boxed a'):
            image = None
            img = result.find('img')
            if img:
                image = img['src']
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title'],
                image=image,
            )

    def _parse_parse_page(self, soup):
        for link in soup.select('div.entry-content a'):
            url = link['href']
            if 'magnet' in url or 'email-protection' in url:
                continue
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=url,
                link_title=link.text,
            )
        for iframe in soup.select('div.entry-content iframe'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=iframe['src'],
            )

