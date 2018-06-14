# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class AvxhomeIn(SimpleScraperBase):
    BASE_URL = 'https://avxhm.se/'
    OTHER_URLS = ['https://soek.be', 'http://avaxhome.unblocker.xyz', 'https://avxhome.se']
    TRELLO_ID = 'gxHUBCXP'
    PAGE = 1

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return None

    def get(self, url, **kwargs):
        return super(AvxhomeIn, self).get(url, allowed_errors_codes=[410,], verify=False, **kwargs)

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'next')
        self.PAGE += 1
        return 'https://soek.be' + link['href'] if link else None

    def _fetch_search_url(self, search_term, media_type):
        self.PAGE = 1
        return self.BASE_URL + '/search?q=' + self.util.quote(search_term)

    def _parse_search_result_page(self, soup):
        results = soup.select('div.panel-heading h3 a')
        if not results and len(results) == 0 and self.PAGE < 2:
            return self.submit_search_no_results()
        for result in results:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.title-link').text.strip()
        for link in soup.select('div.col-lg-9 div.col-lg-12 div.text a'):
            onclick = ''
            try:
                onclick = link['onclick']
            except KeyError:
                pass
            if onclick and 'avxhome' not in link['href'] and 'avaxhome' not in link['href'] and 'http' in link['href'] \
                and 'imdb' not in link['href'] and 'avaxhm' not in link['href']:
                href = link['href']
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=href,
                                         link_title=title,
                                         )