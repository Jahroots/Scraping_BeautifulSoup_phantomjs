# coding=utf-8

import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class JpfilesEu(SimpleScraperBase):
    BASE_URL = 'https://jpfiles.eu'
    OTHER_URLS = ['http://jpfiles.eu']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Sorry, but you are looking for something that isn’t here'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'Next page »')
        if link:
            return link['href']

    def _parse_search_result_page(self, soup):
        find = 0
        for results in soup.select('h2.title a'):
            result = results['href']
            title = results.text.strip()
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            find=1
        if not find:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2.title').text.strip()
        index_page_title = self.util.get_page_title(soup)
        try:
            download_links = soup.find(text=re.compile(u'Download/')).find_all_next('a')
        except AttributeError:
            download_links = soup.find(text=re.compile(u'Download/')).find_all('a')
        for download_link in download_links:
            if 'http' in download_link.text:
                link = download_link.text
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_text=title,
                )
