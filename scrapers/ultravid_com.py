# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import  SimpleScraperBase


class UltraVidCom(SimpleScraperBase):
    BASE_URL = 'http://ultra-vid.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'


        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'next')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.boxitem')
        if not results:
            self.submit_search_no_results()
            return
        for result in results:
            link = result.find('a')
            if not link:
                continue
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.get('title', ''),
                image=self.util.find_image_src_or_none(result, 'img')
            )

    def parse(self, parse_url, **extra):
        # sneaky as hell.
        # 403 forbidden the content to keep bots out, BUT have actual content.
        soup = self.get_soup(
            parse_url,
            allowed_errors_codes=[403]
        )
        index_page_title = self.util.get_page_title(soup)
        for iframe in soup.select('iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe['src']
            )
        for input in soup.select('ol.commentlist a > input[type="button"]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=input.parent.href,
                link_text=input.value,
            )

        for link in soup.select('div.jbox-content a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['href'],
                link_title=link.get('title', link.text),
                )
        for link in soup.select('div#postcontent iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=link.get('title', link.text),
                )
