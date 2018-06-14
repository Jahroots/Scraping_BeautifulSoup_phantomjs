# encoding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin
from sandcrawler.scraper.caching import cacheable


class KinoLiveOrg(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://kinored1.life'
    OTHER_URLS = ['http://kinored.life', 'http://kinolive.red']
    # USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:43.0) Gecko/20100101 Firefox/43.0'
    LONG_SEARCH_RESULT_KEYWORD = 'man'
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for site in (self.BASE_URL, 'http://kino-live2.org', 'http://kino-live.org'):
            self.register_url(ScraperBase.URL_TYPE_SEARCH, site)
            self.register_url(ScraperBase.URL_TYPE_LISTING, site)


    def post(self, url, **kwargs):
        # Inject usre agent into all gets.
        # if 'headers' not in kwargs:
        #     kwargs['headers'] = {}
        # kwargs['headers']['User-Agent'] = self.USER_AGENT
        return super(self.__class__, self).post(url, allowed_errors_codes=[403], **kwargs)

    def get(self, url, **kwargs):
        # Inject user agent into all gets.
        # if 'headers' not in kwargs:
        #     kwargs['headers'] = {}
        # kwargs['headers']['User-Agent'] = self.USER_AGENT
        return super(self.__class__, self).get(url, allowed_errors_codes=[403], **kwargs)



    def _fetch_no_results_text(self):
        return u'поиск по сайту не дал никаких'

    def _parse_search_result_page(self, soup):
        # Find the h1 links, then iterate through siblins to get the rest
        #  of the info

        for result in soup.select('div[data-link]'):

            self.submit_search_result(
                link_url=result['data-link'],
                link_title=result.text,
            )
        nextlink = soup.select('div.pages a#nextlink')
        if nextlink and self.can_fetch_next():
            self.page += 1
            self.log.debug('--------------- %d ---------------' % self.page)
            self._parse_search_result_page(self._get_search_results(self.search_term, self.page))

    @cacheable()
    def _extract_iframe(self, url):
        soup = self.get_soup(u'{}{}'.format(self.BASE_URL, url))
        video = soup.select_one('video source')
        if video:
            return video['src']
        return None

    def _parse_parse_page(self, soup):
        # Find our flashvars param,t hen grab either the file, or the
        # playlist from within.
        iframes = soup.select('article.full-page iframe')
        for iframe in iframes:
            if iframe['src'].startswith('/play'):
                src = self._extract_iframe(iframe['src']) or None
            else:
                src = iframe['src']
            if src:
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=src,
                    )

