# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Rlslog(SimpleScraperBase):
    BASE_URL = 'http://www.rlslog.net'
    OTHER_URLS = [
        'http://rlslog.net',
        'http://www.rlslog.me',
        'http://rls-logs.com',
        'http://rlsslog.com',
        'http://nitrodl.com',
        'http://tinyddl.com'
    ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)


        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return 'Sorry, no posts matched your criteria'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'Next Page »')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.findAll('a', rel='bookmark'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('.entry h3').text.strip()

        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('.entrybody a'):
            if not link.parent:
                continue
            if 'Download' in link.parent.text and \
                not link.text.startswith(self.BASE_URL) and \
                link.href.startswith('http'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=title
                    )

        # links in comments
        for link in soup.select('.commenttext a'):
            if link.attrs.get('rel', '') == ['nofollow']:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link['href'],
                    link_title=title
                    )
