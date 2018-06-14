# coding=utf-8

from sandcrawler.scraper import SimpleScraperBase, ScraperBase


class MajaaNet(SimpleScraperBase):
    BASE_URL = 'http://majaa.mobi'

    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(self.MEDIA_TYPE_FILM)
        self.register_media(self.MEDIA_TYPE_TV)

        self.register_url(
            self.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            self.URL_TYPE_LISTING,
            self.BASE_URL)

    def get(self, url, **kwargs):
        return super(MajaaNet, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def _fetch_no_results_text(self):
        return

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next Page »')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '?s={}'.format(search_term)

    def _parse_search_result_page(self, soup):
        found = False
        for link in soup.select('.entry-content .post-title a'):
            found = True
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text
            )
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h3.post-title')
        if title:
            title = title.text
        links = soup.select('.entry-content p a')
        for link in links:
            if self.BASE_URL not in link.href:
                self.submit_parse_result(index_page_title= self.util.get_page_title(soup),
                                         link_title=title,
                                         link_url=link.get('href'))
