# -*- coding: utf-8 -*-

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class TelechargementzTv(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.2017.telechargementz.tv'
    OTHER_URLS = [
        'http://www.t411.telechargementz.tv',
        'http://www.film.telechargementz.tv',
        'http://www.stream.telechargementz.tv'
        'http://www.zone.telechargementz.tv',
        'http://www.gratuit.telechargementz.tv'
    ]

    LONG_SEARCH_RESULT_KEYWORD = 'man'

    def setup(self):
        raise NotImplementedError('Deprecated, website becomes an ads page')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_ALL)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'La recherche n a retourné aucun résultat'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.post-title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.split('|')[0],
            )
        # Seems to change sometimes...
        for result in soup.select('h2.title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text.split('|')[0],
            )

    def _parse_parse_page(self, soup):

        title = soup.select_one('div.post-title')
        if title and title.text:
            title = title.text.split('|')[0].strip()

        links_a = soup.find('div', 'title')
        if links_a:
            links_a = links_a.find_all('a', text=u'Télécharger')
        else:
            links_a = None

        movie_link = ''
        if links_a:
            noindex_links = soup.find_all('a', text=u'Regarder Streaming') + links_a
            for noindex_link in noindex_links:
                if 'streaming' in noindex_link['href']:
                    movie_link = self.get_soup(noindex_link['href']).find('iframe')
                    if movie_link and movie_link['src']:
                        movie_link = movie_link['src']
                else:
                    movie_link = self.get_soup(noindex_link['href']).find('div', id='hideshow')
                    if movie_link:
                        movie_link = movie_link.find('a')
                        if movie_link and movie_link['href']:
                            movie_link = movie_link['href']

                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=movie_link,
                    link_title=title
                )