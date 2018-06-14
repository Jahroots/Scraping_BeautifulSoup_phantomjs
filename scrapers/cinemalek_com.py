# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class Cinemalek(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://cinemalek.net'
    OTHER_URLS = ['https://cinmastar.com', 'http://cinemalek.com', 'https://cinmastar.online']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'
    times = 0
    ALLOW_FETCH_EXCEPTIONS = True

    def setup(self):
        super(Cinemalek, self).setup()
        self._request_response_timeout = 600
        self._request_connect_timeout = 400

    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        link = None
        try:
            link = soup.find('a', text=u'التالي ›')['href']
        except TypeError:
            pass
        return link if link else None

    def parse(self, parse_url, **extra):
            parse_url = parse_url + '?watch=1'
            soup = self.get_soup(parse_url)
            self._parse_parse_page(soup)

    def _parse_search_result_page(self, soup):
        blocks = soup.select('div.w-1200 div.block_loop')
        if not blocks:
            return self.submit_search_no_results()
        for block in blocks:
            page_link = block.find('a')['href']
            title = block.find('a').text.strip()
            self.submit_search_result(
                    link_url=page_link,
                    link_title=title,
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        temp_link = soup.select_one('div.redirect a')
        soup = self.get_soup(temp_link.href)
        links = soup.select('ul#recent_intery a')
        for url in links:
            soup = self.get_soup(url.href)
            iframe = soup.select_one('#DataServers iframe')
            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=iframe['src'])


