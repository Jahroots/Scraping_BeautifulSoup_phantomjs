# coding=utf-8

from sandcrawler.scraper import ScraperBase, ScraperParseException
from sandcrawler.scraper import SimpleScraperBase


class Urgrove(SimpleScraperBase):
    BASE_URL = "http://urgrove.com"

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        raise NotImplementedError('TODO - captcha')

        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'There are no posts to display here'

    def _parse_search_result_page(self, soup):
        for result in soup.select(".postinfo h3 a"):
            self.submit_search_result(link_title=result.text,
                                      link_url=result.get('href'))

    def _fetch_next_button(self, soup):
        self.log.debug('----------------------')
        link = soup.select_one("#previousposts a")
        if link:
            return link['href']

    def _parse_parse_page(self, soup):
        title = soup.select_one('#pagecontent h1').text
        raise ScraperParseException('TODO - captcha')
