# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class Fullhd720pizleCom(SimpleScraperBase):
    BASE_URL = 'http://www.fullhd720pizle1.net'
    OTHERS_URLS = ['http://www.fullhd720pizle1.com', 'http://www.fullhd720pizle.org', 'http://www.fullhd720pizle.net']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        super(self.__class__, self).setup()
        self._request_connect_timeout = 300
        self._request_response_timeout = 400


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?arama={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Aradığınız kelimeyi tekrar arayarak bulabilirsiniz'

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403,], **kwargs)

    def _fetch_next_button(self, soup):
        next_link = soup.select_one('a.nextpostslink')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('div.filmcontent div.moviefilm a'):
            self.submit_search_result(
                link_url=results['href'],
                link_title=results.text,
                image=self.util.find_image_src_or_none(results, 'img')
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('#kendisi iframe[allowfullscreen]'):
            movie_link = link['src']
            self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link,
                        link_text=title,
                    )