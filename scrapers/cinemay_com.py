# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import re


class CinemayCom(SimpleScraperBase):
    BASE_URL = 'http://streaming.cinemay.com'
    OTHER_URLS = ['http://2018.cinemay.com', 'http://2017.cinemay.com', 'http://www.cinemay.com']
    TRELLO_ID = '6zEns9L9'
    LONG_SEARCH_RESULT_KEYWORD = '2017'
    SEARCH_TERM = ''
    PAGE = 1

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "fra"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        self.PAGE = 1
        self.SEARCH_TERM = search_term
        return self.BASE_URL + '/?s={}'.format(search_term.replace(' ', '+').lower())

    def _fetch_next_button(self, soup):
        self.PAGE += 1
        return self.BASE_URL + '/page/{}/?s={}'.format(self.PAGE, self.SEARCH_TERM.replace(' ', '+').lower())

    def get(self, url, **kwargs):
        return super(CinemayCom, self).get(url, allowed_errors_codes=[404,], **kwargs)

    def _parse_search_results(self, soup):
        results = soup.select('div.items article div.poster a')
        if not results and len(results) == 0 and self.PAGE < 2:
            return self.submit_search_no_results()

        for link in results:
            title = link.text
            page_soup = self.get_soup(link['href'])
            # Feels a bit general, but should be ok; basically all links in the
            # linked area.
            for movie_link in page_soup.select(
                    'ul.episodios div.episodiotitle a'):
                if movie_link['href'] != '#':
                    url = movie_link['href']
                    if not url.startswith('http'):
                        url = self.BASE_URL + url
                    self.submit_search_result(
                        link_url=url,
                        link_title=(title + " " + movie_link.text).strip()
                    )

        next_button = self._fetch_next_button(soup)

        if next_button and self.can_fetch_next():
            self.log.debug('----------------')
            self._parse_search_results(
                self.get_soup(
                    next_button)
            )


    def parse(self, page_url, **extra):
        soup = self.get_soup(page_url)
        self._parse_parse_page(soup)


    def _parse_parse_page(self, soup):
        text = soup.find('script', text=re.compile('id:.+\,')).text
        id = text.split('id: "')[1].split('",')[0].strip()
        soup = self.get_soup('{}/playery/?id={}'.format(self.BASE_URL, id))

        for result in soup.select('iframe'):
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=result['src'],
                                     )

        for result in soup.select('input[name="videov"]'):
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=self.BASE_URL + result['value'],
                                     )