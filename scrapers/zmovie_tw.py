# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class ZMovieTw(SimpleScraperBase):
    BASE_URL = 'http://www.zmovie.tw'
    OTHER_URLS = ['http://www.zmovie.co', 'http://www.zmovie.link', 'http://www.zmovie.se']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return 'Sorry no movie found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=' Next+')
        if link:
            return link['href']
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/title/%s/1' % \
                               self.util.quote(search_term)

    def _parse_search_result_page(self, soup):
        # Hardly a css tag to be found!
        # Instead find unique images with 'alt="Watch movie ...'
        added = set()
        for img in soup.findAll('img', {'alt': re.compile('^Watch  movie')}):
            if img['src'] in added:
                continue
            link = img.parent
            self.submit_search_result(
                link_url=link['href'],
                link_title=link['title'],
                image=img['src'],
            )
            added.add(img['src'])

    def _parse_parse_page(self, soup):
        for link in soup.select('a.atest'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     )
