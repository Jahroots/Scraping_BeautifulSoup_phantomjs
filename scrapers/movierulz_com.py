#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class MovieRulzCom(SimpleScraperBase):
    BASE_URL = 'http://www.movierulz.gr'
    OTHERS_URLS = ['http://www.movierulz.so', 'http://www.movierulz.tv']


    def setup(self):
        raise NotImplementedError('deleted duplicated scraper. the othe one is movierulz_to.py')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, 'http://www.movierulz.com']:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return 'This might because it no longer exists or we have moved it'

    def _fetch_next_button(self, soup):
        link = soup.select('div.nav-older a')
        if link:
            return link[0]['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.cont_display a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title'],
                image=result.find('img')['src']
            )

    def _parse_parse_page(self, soup):
        # XXXX Several of these go to other sites that aren't the
        # end source, just another embedding site... 
        for link in soup.select('div.entry-content a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     link_title=link.text,
                                     )

