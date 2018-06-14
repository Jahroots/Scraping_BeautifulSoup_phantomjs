# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FileCatch(SimpleScraperBase):
    BASE_URL = 'http://filecatch.com'

    SINGLE_RESULTS_PAGE = True  # in reality - no

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ]:  # + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.proxy_region = 'nl'  # at least not US!

        self._request_connect_timeout = 60
        self._request_response_timeout = 120

    def search(self, search_term, media_type, **extra):
        soup = self.get_soup(self._fetch_search_url(search_term, media_type))

        if not soup.select('#search_paging a'):
            self.submit_search_no_results()
            return

        max_page_num = int(soup.select('#search_paging a')[-1].href.split('&p=')[1])

        for page in range(1, max_page_num + 1):
            if not self.can_fetch_next():
                continue
            if page > 1:
                soup = self.get_soup(self._fetch_search_url(search_term, media_type, page=page))
            for link in soup.select('.btn.icon.adddwnl'):
                self.submit_search_result(link_title=link.attrs['title'][10:],
                                          link_url=self._fetch_search_url(search_term, media_type, page=page))

                # self.submit_parse_result(link_title=link.attrs['title'][10:],
                #                          link_url=link['href']
                #                          )
            self.log.debug('-----------------')

    def _fetch_no_results_text(self):
        return u' No files found.'

    def _fetch_search_url(self, search_term, media_type, page=1):
        return self.BASE_URL + '/?q=' + self.util.quote(search_term) + ('&p=%s' % page if page > 1 else '')

    def _parse_parse_page(self, soup):
        for link in soup.select('.btn.icon.adddwnl'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(), link_title=link.attrs['title'][10:],
                                     link_url=link['href']
                                     )
