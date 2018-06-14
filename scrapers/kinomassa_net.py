# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin

class KinomassaNet(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://kinomassa.biz'
    OTHER_URLS = ['http://kinomassa.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]


    def _parse_search_result_page(self, soup):
        for result in soup.select('div[class="shortfilm sear"]'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=  link.href,
                link_title=link.text,
                image= self.BASE_URL  + self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.boxvideo object param[name="flashvars"]'):
            src = link['value'].split('http')[2]

            if src.find('http') == -1:
                src = 'http' + src
                
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=src,
                link_title=link.text,
            )
