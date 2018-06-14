# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin

class KinozadrotClub(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.kinokiller.club'
    OTHER_URLS = ['http://kinozadrot.club']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        super(self.__class__, self).setup()
        self.encode_search_term_to = 'cp1251'

    def _parse_search_result_page(self, soup):
        for result in soup.select('article.film-item'):
            link = result.select_one('a')
            if link and link.has_attr('href'):
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for meta in soup.select('meta'):
            if meta.get('property', '') == 'og:video' and \
                meta.get('content'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=meta.get('content')
                )

