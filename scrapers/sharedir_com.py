#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class ShareDirCom(SimpleScraperBase):

    BASE_URL = 'https://sharedir.com'
    #USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) ' \
     #   'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 ' \
     #   'Safari/537.36'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self._request_connect_timeout = 400
        self._request_response_timeout = 400


    def _fetch_no_results_text(self):
        return 'No results containing all your search terms were found.'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?s=' + \
            self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        if link:
            return self.BASE_URL + link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('a.big'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        # Suck the info out of the 'directlinks' section - saves going through
        # their obfuscator.  Heh.
        for dirlinks in soup.select('pre#dirlinks'):
            for link in dirlinks.text.strip().split('\n'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link
                                         )

