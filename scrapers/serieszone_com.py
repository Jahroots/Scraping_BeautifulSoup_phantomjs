# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin

class SerieszoneCom(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://serieszone.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return None#u'Lo sentimos, pero que esta buscando algo que no esta aqui.'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one(' TODO ')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        results= soup.select('div[class="post bar hentry"] h3 a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('p iframe'):
            src = link['src']

            if src.find('http') == -1:
                src = 'http:' + src

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=src,
                link_title=link.text,
            )
