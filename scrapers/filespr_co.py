# coding=utf-8

from sandcrawler.scraper import ScraperBase, ScraperFetchException
from sandcrawler.scraper import SimpleScraperBase


class FilesPrCo(SimpleScraperBase):
    BASE_URL = 'http://www.filespr.info'

    OTHER_URLS = ['http://www.filesprr.com', 'http://www.filespr.biz']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"
        raise NotImplementedError('the domain is deprecated')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):
        try:
            soup = self.get_soup(self._fetch_search_url(search_term, media_type), allowed_errors_codes=[404])
            self._parse_search_results(soup)
        except ScraperFetchException:
            self.submit_search_no_results()

    def _fetch_no_results_text(self):
        return 'did not match any documents.'

    def _fetch_search_url(self, search_term, media_type):
        search_term = self.util.quote(search_term)
        return '{}/{}/{}'.format(self.BASE_URL, search_term[0], search_term)

    def _fetch_next_button(self, soup):
        curr_page_link = soup.select_one('.str span')
        if curr_page_link.parent.find_next_sibling():
            self.log.debug('----------------')
            return self.BASE_URL + curr_page_link.parent.find_next_sibling().a.href

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.info2 a')[1:]:
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):
        for textarea in soup.select('textarea#copy-links'):
            for link in textarea.text.strip().split('\n'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link
                                         )
