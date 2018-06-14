# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import re


class PutlockerLive(SimpleScraperBase):
    BASE_URL = 'https://putlocker7.live'
    OTHER_URLS = ['https://putlocker1.live', 'http://putlockerr.live','http://putlocker.live/', 'http://putlocker.watch/',
                  'https://putlockerx.live']
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _do_search(self, search_term):
        return self.post_soup(
            self.BASE_URL + '/search_movies',
            data={'q':search_term,
                  'submit':'Search Now!'
                  }
        )

    def search(self, search_term, media_type, **extra):
        page = self._do_search(search_term)
        if page.find(text=re.compile('Here >>>')):
            return self.submit_search_no_results()
        self._parse_search_result_page(page)

    def _parse_search_result_page(self, soup):
        for td in soup.select('div.table div'):
            link = td.find('a')['href']
            if not link:
                continue
            title = td.find('a')['title']
            self.submit_search_result(
                link_title=title,
                link_url=link
            )

    def _parse_parse_page(self, soup):
        movie_link_src = soup.text.split('var locations = ["')[-1].split('"]')[0].replace('\\', '')
        movie_link_base = movie_link_src.split('emb.')[0]
        id_num = movie_link_src.split('html?')[-1].split('=')[0]
        movie_link = movie_link_base+'embed-'+id_num+'.html'
        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                 link_url=movie_link)