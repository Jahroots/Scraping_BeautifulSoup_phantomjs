# coding=utf-8

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class OnlineFreebeeRu(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://online-freebee.ru'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for site in self.BASE_URL, 'http://online-freebee.ru':
            self.register_url(ScraperBase.URL_TYPE_SEARCH, site)
            self.register_url(ScraperBase.URL_TYPE_LISTING, site)

    def _fetch_search_url(self, search_term):
        return self.BASE_URL


    def get(self, url, **kwargs):
        return super(OnlineFreebeeRu, self).get(url, **kwargs)

    def post(self, url, **kwargs):
        return super(OnlineFreebeeRu, self).post(url, **kwargs)

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов.'

    def search(self, search_term, media_type, **extra):
        self.get(self.BASE_URL)
        return super(OnlineFreebeeRu, self).search(search_term, media_type, **extra)

    def _parse_search_result_page(self, soup):
        for result in soup.select('.sheading a'):
            # image = result.parent.parent.select('div.maincont img')[0]
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
                # image=self.BASE_URL + image['src'],
            )

    def _parse_parse_page(self, soup):
        # XXX There was a trick on one of these pages, but I only found it
        # once and can't find it again.
        # Looked like it loads a dead, static VK not found movie, then
        #  dynamically loads another video on top of that!
        # Everything else I can find is just embedded iframes.
        for iframe in soup.select('div.maincont iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=iframe['src'],
                                     )
