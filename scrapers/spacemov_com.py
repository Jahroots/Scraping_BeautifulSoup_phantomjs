# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class SpacemovCom(SimpleScraperBase):
    BASE_URL = 'https://spacemov.is'
    OTHER_URLS = ['https://spacemov.org', 'https://spacemov.io', 'http://spacemov.io','https://spacemov.tv', 'https://spacemovhd.com', 'https://www.spacemov.tv', 'https://www.spacemov.net', 'http://www.spacemov.ag', ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search-query/{}/'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Next →')
        return next_link['href'] if next_link else None

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _parse_search_result_page(self, soup):

        results = soup.select('div[class="movies-list movies-list-full"] div.ml-item a.ml-mask')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for results in results:

            result = results['href']
            title = results.text
            if not title:
                title = result.strip('/').split('/')[-1].replace('-',' ').split('full movie')[0]
            self.submit_search_result(
                link_url=result,
                link_title=title
            )


    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url + '/watching/')
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        #self.log.debug(soup)
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)

        results = soup.select('#servers-list li[data-drive]')
        for result in results:
            movie_link = result['data-drive']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )