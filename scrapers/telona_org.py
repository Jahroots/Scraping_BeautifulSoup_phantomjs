# coding=utf-8

from sandcrawler.scraper import SimpleScraperBase, ScraperBase


class Telona(SimpleScraperBase):
    BASE_URL = 'http://baixeturbofilmes.com'
    OTHERS_URLS = ['http://www.telona.org']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = "por"

        self.register_media(self.MEDIA_TYPE_FILM)
        self.register_media(self.MEDIA_TYPE_TV)

        self.register_url(self.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(self.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return '" did not match'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        # No 'no results' message - just check for a lack of reslts.
        results = soup.select('.bp-head h2 a')
        if not results:
            return self.submit_search_no_results()
        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.post-tile.entry-title').text.strip()

        for link in soup.select('.entry-content p a'):
            url = link.href.split('/css/?')[1][::-1] if '/css/?' in link.href else link.href
            if url:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                     link_title=title
                                     )
