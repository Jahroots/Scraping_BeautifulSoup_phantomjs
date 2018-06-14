# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin


class LetitfilmsCom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://letitfilms.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = '2016'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div h3'):
            link = result.select_one('a[href*="' + self.BASE_URL + '"]')
            if link:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('span a[target="_blank"]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
            )
