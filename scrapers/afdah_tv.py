# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.caching import cacheable
import re


class AfdahTv(SimpleScraperBase):
    BASE_URL = 'http://afdah.to'
    OTHER_URLS = ['http://afdah.tv']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True



    def setup(self):
        super(AfdahTv, self).setup()
        self.requires_webdriver = True
        self.webdriver_type = 'chrome'
        self.adblock_enabled = False

    @cacheable()
    def _get_search_term_encrypted(self, search_term):
        self.webdriver().get(self.BASE_URL)
        return self.webdriver().execute_script("""
            return CryptoJS.AES.encrypt("%s|||title", "Watch Movies Online").toString();
        """ % search_term)

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/wp-content/themes/afdah/ajax-search2.php'

        soup = self.post_soup(
            search_url,
            data={'process':self._get_search_term_encrypted(search_term)}
        )
        self.log.warning(soup)
        self._parse_search_results(soup)

    def _fetch_no_results_text(self):
        return u'Displaying top 0 results'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        for link in soup.select('li a'):
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
            )

    @cacheable()
    def _get_embedded_source(self, url):
        self.webdriver().get(url)
        content = self.webdriver().page_source
        soup = self.make_soup(content)
        results = []
        for file in re.findall('file: "(.*?)"', content):
            results.append(file)
        for iframe in soup.select('iframe'):
            results.append(iframe['src'])
        self.log.debug('From %s found %s', url, results)
        return results

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        done = set()
        for link in soup.select('div.tabContent a'):
            if not link.href.startswith('http'):
                continue
            if link.href.startswith(self.BASE_URL):
                if 'embed' not in link.href:
                    self.log.warning('Found not-embed link: %s', link.href)
                    continue
                if link.href not in done:
                    for result in self._get_embedded_source(link.href):
                        self.submit_parse_result(
                            link_url=result,
                            index_page_title=index_page_title,
                        )
                    done.add(link.href)

            else:
                self.submit_parse_result(
                    link_url=link.href,
                    index_page_title=index_page_title,
                )
