# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class FreeMoviesStreaming(SimpleScraperBase):
    BASE_URL = 'http://www.freemoviesstreaming.net'
    OTHER_URLS = []

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'
        raise NotImplementedError('the website is out of reach')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'No posts found. Try a different search?'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='»')
        self.log.debug('------------------------')
        return next['href'] if next else None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('.title h2 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select('.title h1')[0].text.replace(' streaming', '').strip()

        self.submit_parse_result(
            index_page_title=soup.title.text.strip(),
            link_url=soup.select('.text-box p a')[0].href,
            link_title=title,
        )
