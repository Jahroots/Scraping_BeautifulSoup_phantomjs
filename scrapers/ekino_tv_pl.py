# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.caching import cacheable
import re


class EkinoTvPl(SimpleScraperBase):
    BASE_URL = 'http://ekino-tv.pl'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'pol'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    REQUIRES_WEBDRIVER = ('parse', )
    WEBDRIVER_TYPE = 'phantomjs'

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/search',
                data={
                    'search_field': search_term,
                }
            )
        )

    def _parse_search_results(self, soup):
        found = 0
        for result in soup.select('div.title a'):
            link = self.BASE_URL+result['href']
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    @cacheable()
    def _follow_link(self, url):
        wd = self.webdriver()
        wd.get(url)
        soup = self.make_soup(
            wd.page_source
        )
        iframe = soup.select_one('iframe')
        if iframe:
            return iframe['src']
        return None

    def _parse_parse_page(self, soup):

        for link in soup.select('div.tab-pane a'):
            try:
                onclick = link['onclick']
            except KeyError:
                pass
            else:
                for domain, id in re.findall(
                    "ShowPlayer\('(.*)','(.*)'\)",
                    onclick):
                    url = self._follow_link(
                        '{}/watch/f/{}/{}'.format(self.BASE_URL, domain, id)
                    )
                    if url:
                        self.submit_parse_result(
                            index_page_title=self.util.get_page_title(soup),
                            link_url=url
                        )
