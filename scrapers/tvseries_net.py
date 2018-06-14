# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TVseries_net(SimpleScraperBase):
    BASE_URL = 'http://tvseries.net'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        raise NotImplementedError('This site requires payments to watch.')

        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _login(self):
        self.post(self.BASE_URL + '/chkpass.php?from=http%3A%2F%2Ftvseries.net%2Fsearch.php',
                  data=dict(uname_signin='sands8', pword_signin='crawl8', button='Login'))

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self.BASE_URL + '/search.php', data=dict(keyword=search_term))
        self._parse_search_results(soup)

    def _fetch_no_results_text(self):
        return

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'»')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('#top1 tr td table tr td a img'):
            self.submit_search_result(
                link_url=result.parent['href'],
                link_title=result.parent['title'],
            )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        self._login()

        series = soup.select('#urltb li a')
        for ser in series:
            # ser_soup = self.get_soup(ser.href)
            # self._parse_iframes(ser_soup, css_selector='div.iframe iframe')
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=self.BASE_URL + ser.href,
                                     link_title=soup.title.text.strip()
                                     )
