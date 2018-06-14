# coding=utf-8

from sandcrawler.scraper import SimpleScraperBase, ScraperBase


class Topdezfilmes(SimpleScraperBase):
    BASE_URL = 'http://topdezfilmes.org'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = "spa"

        self.register_media(self.MEDIA_TYPE_FILM)
        # self.register_media(self.MEDIA_TYPE_TV)

        self.register_url(self.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(self.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Nada Encontrado'

    def _fetch_next_button(self, soup):
        next = soup.select_one('.span6.next-post a')
        self.log.debug('---------------')
        return next['href'] if next else None

    def _parse_search_result_page(self, soup):
        # No 'no results' message - just check for a lack of reslts.
        results = soup.select('.entry-title a')
        if not results:
            return self.submit_search_no_results()
        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.entry-title').text.strip()

        for link in soup.select('.entry-content p span strong span a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link.href,
                                     link_title=title
                                     )
