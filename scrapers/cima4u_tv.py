# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase


class Cima4uTv(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://cima4u.tv'
    LONG_SEARCH_RESULT_KEYWORD = 'man'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'ara'


        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'الصفحة التالية «')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = False
        for result in soup.select('div#dataTab a'):
            found = True
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        link = soup.find('a','button button--aylen button--border-thin button--round-s')['href']
        movie_soup = self.get_soup(link)
        movie_link = ''
        try:
            movie_link = movie_soup.find('a', 'get-embed')['data-link']
        except AttributeError:
            pass
        embed_soup = self.get_soup(movie_link)
        downloads_data = embed_soup.select('a.sever_link')
        for download_data in downloads_data:
            data_link = download_data['data-link']
            links_soup = self.post_soup('http://live.cima4u.tv/structure/server.php?id='+data_link, data={'id':'{}'.format(data_link)})
            url = links_soup.find('iframe')['src']
            self.submit_parse_result(index_page_title=self.util.get_page_title(movie_soup),
                                     link_url=url,
                                     )
        download_url = movie_soup.find('a', 'download_link')['href']
        self.submit_parse_result(index_page_title=self.util.get_page_title(movie_soup),
                                 link_url=download_url,
                                 )
