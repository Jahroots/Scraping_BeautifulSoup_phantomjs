#coding=utf-8

import time
from sandcrawler.scraper import SimpleScraperBase, ScraperBase
from sandcrawler.scraper import ScraperFetchException, ScraperFetchProxyException

from sandcrawler.scraper.caching import cacheable

class GeneralFilEs(SimpleScraperBase, ScraperBase):
    """
    Notes
     This scraper may have search results submitted from general_search_com.
     This page has a search itself, as well as handling results from the other
     scraper.
    """

    BASE_URL = 'http://www.generalfil.es'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    has_any = False

    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH,  self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


    def _fetch_no_results_text(self):
        return None#u'- 0 results'

    def _fetch_search_url(self, search_term, media_type):
        self.has_any = False
        return self.BASE_URL + '/files-m/%s/?qa=%s&filter=_Video_' % (self.util.quote(search_term),
                                                                              self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'next»')
        return self.BASE_URL+link['href'] if link else None

    def _parse_search_result_page(self, soup):
        result_list = soup.select('#gf_files li h2.title a')

        if not result_list or len(result_list) == 0 and not self.has_any:
            return self.submit_search_no_results()

        for result in result_list:
            if result.get('id') == 'sponsored':
                self.log.debug('Skipping sponsored result.')
                continue
            link = result['href']
            title = result['title']
            self.submit_search_result(
                        link_url=link,
                        link_title=title
            )
            self.has_any = True

    @cacheable()
    def _follow_link(self, url):
        time.sleep(3)
        return self.get(url, allow_redirects=False).headers.get('Location', url)



    def _parse_parse_page(self, soup):
        link = soup.select_one('a#gf-download-button')
        if link:
            url = link['href']
            if url.startswith('/go/'):
                print self.BASE_URL + url
                url = self._follow_link(self.BASE_URL + url)
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=url,
                link_title=link.text.strip(),
                )
