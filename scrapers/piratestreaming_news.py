# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PiratestreamingNews(SimpleScraperBase):
    BASE_URL = 'http://www.piratestreaming.black'
    OTHER_URLS = ['http://www.piratestreaming.news']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    done = True

    def _fetch_no_results_text(self):
        return u'Nessun Risultato'

    def _fetch_search_url(self, search_term, media_type=None, start=0):
            if 'film' in media_type:
                self.start = start
                self.search_term = search_term
                return self.BASE_URL + '/cerca.php?pageNum_cerca_film={}&all={}&SearchSubmit='.format(start, search_term)
            if 'tv' in media_type:
                self.start = start
                self.search_term = search_term
                return self.BASE_URL + '/cerca.php?pageNum_cerca_serietv2={}&all={}&SearchSubmit='.format(start, search_term)

    def search(self, search_term, media_type, **extra):
        self.done =True
        super(self.__class__, self).search(search_term, media_type)

    def _parse_search_results(self, soup):
        results = soup.select('div.featuredItem a[href*=".html"]')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)
        if self.start == 0:
           self.start = 1
        self.start += 1
        for m_type in self.MEDIA_TYPES:
            next_button_link = self._fetch_search_url(self.search_term, media_type=m_type, start=self.start)
            if next_button_link and self.can_fetch_next() and self.done:
                self._parse_search_results(
                    self.get_soup(
                        next_button_link
                    )
                )

    def _parse_search_result_page(self, soup):
        results = soup.select('div.featuredItem a[href*=".html"]')
        if not results or len(results) == 0:
            self.done = False
            return self.submit_search_no_results()

        for link in soup.select('div.featuredItem'):
            link = link.select_one('a[href*=".html"]')
            if link:
                if '/serietv/' in link['href']:
                    self.submit_search_result(
                        link_title=link.text,
                        link_url=link.href
                    )
                if '/film/' in link['href']:
                    self.submit_search_result(
                        link_title=link.text,
                        link_url=link.href
                    )

    def _parse_parse_page(self, soup):
        title = soup.find('h1', 'title').text.strip()
        for link in soup.find('div', 'featuredContent').find_all('a', attrs={'rel':'nofollow'}):
            url = link['href']
            if 'piratestreaming' not in url and 'youtube' not in url and 'qertewrt' not in url:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_title=title,
                                         link_url=url)