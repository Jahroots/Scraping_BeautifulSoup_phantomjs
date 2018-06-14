# coding=utf-8

import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class XrysoiSe(SimpleScraperBase):
    BASE_URL = 'https://xrysoi.online'
    OTHER_URLS = ['http://xrysoi.se']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'gre'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Η ταινία που αναζητήσατε δεν βρέθηκε.'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='»')
        self.log.debug('---------------')
        return next['href'] if next else None

    def _parse_search_result_page(self, soup):
        find = 0
        for results in soup.select('div.movief a'):
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            find=1
        if not find:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1')
        if title:
            title = title.text.strip()
        index_page_title = self.util.get_page_title(soup)
        download_links= soup.select('div.filmicerik a')
        for download_link in download_links:
            if '.jpg' in download_link['href'] or '.png' in download_link['href'] or 'blogger' in download_link['href']:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=download_link['href'],
                link_text=title,
            )
        iframe_links = soup.select('div.filmicerik iframe')
        for iframe_link in iframe_links:
            if 'youtube' in iframe_link['src']:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe_link['src'],
                link_text=title,
            )
