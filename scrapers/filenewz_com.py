#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FileNewzCom(SimpleScraperBase):

    BASE_URL = 'http://filenewz.xyz'

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

    def _fetch_no_results_text(self):
        return 'Sorry, no downloads found.'

    @property
    def current_page(self):
        if not hasattr(self, '_current_page'):
            self._current_page = 1
        return self._current_page

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/files/all/%s/%s/' % \
            (self.util.quote('-'.join(search_term.split())), self.current_page)

    def _fetch_next_button(self, soup):
        # No next button - keep a stateful page.
        pagination = soup.find('div', {'id': 'pagination'})
        link = pagination.find('a', text=str(self.current_page + 1))
        if link:
            self._current_page += 1
            return self.BASE_URL + link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.result h2 a'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text.strip(),
            )

    def _parse_parse_page(self, soup):
        for textarea in soup.select('p.textarea textarea'):
            for link in textarea.text.strip().split('\n'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link
                                         )
