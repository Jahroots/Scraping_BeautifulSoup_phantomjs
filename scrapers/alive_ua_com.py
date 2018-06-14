# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin
from sandcrawler.scraper.caching import cacheable

class AliveUaCom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://alive-ua.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = '2016'
    FIRST_TIME = True

    USER_AGENT_MOBILE = False

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов.'

    def _parse_search_result_page(self, soup):
        for result in soup.select('span.slink2 a'):
            link = result
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def parse(self, parse_url, **extra):
        self.parse_url = parse_url
        super(AliveUaCom, self).parse(parse_url, **extra)

    @cacheable()
    def _follow_link(self, link):
        return self.get_redirect_location(
            link,
            headers={'Referer': self.parse_url}
        )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)

        for link in soup.select('div.quote a[href*="/engine/go.php"]'):
            try:
                # Sometimes this just fails
                src = self._follow_link(link.href)
            except Exception, e:
                self.log.warning('Failed to follow %s on %s', link.href, self.parse_url)
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=src,
                link_title=link.text,
            )
