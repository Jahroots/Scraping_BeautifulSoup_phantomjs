# coding=utf-8

from sandcrawler.scraper import ScraperBase


class Ch131Me(ScraperBase):
    BASE_URL = 'http://www.seriescoco.me'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        raise NotImplementedError

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/?s=%s' % self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        if unicode(soup).find(
                u'gave no matches') >= 0:
            return self.submit_search_no_results()
        for result in soup.select('div.post h3 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )

        next_button = soup.find('a', text='« Older entries')
        if next_button and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(next_button['href'])
            )

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        for frame in soup.select('div.contenttext iframe'):
            if not frame.get('src', '').startswith('//ads'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=frame.get('src'))

        # A bit dodgy - looks like the site owner comments his urls. Woo.
        for result in soup.select('div.comment a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=result['href'],
                                     )
