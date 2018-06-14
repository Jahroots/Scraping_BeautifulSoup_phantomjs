# -*- coding: utf-8 -*-

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class StreamDownOrg(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://2018.planet-series.co'
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    OTHER_URLS = [
        'http://www.telecharger.planet-series.co',
        'http://www.planet-series.co',
        'http://www.telechargement.planete-series.info/',
        'http://www.telecharger.planete-series.info/',
        'http://www.stream-telecharger.net',
        'http://www.stream-telecharger.com',
        'http://www.stream-down.org',
        'http://www.planete-series.tv',
        'http://www.telecharger.planet-series.co',
        'http://www.planet-series.co',
        'http://www.planete-series.info',
        'http://www.telechargement.planete-series.info'
    ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.media_type_to_category = 'film 0, tv 0'
        self.showposts = 0

    def post(self, url, **kwargs):

        return super(StreamDownOrg, self).post(url, allowed_errors_codes=[404], **kwargs)

    def _fetch_no_results_text(self):
        return u'La recherche n a retourné aucun résultat.'

    def _parse_search_result_page(self, soup):
        for result in soup.select('article.post h2.title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        img = self.util.find_image_src_or_none(soup, 'span#post-img img')
        index_page_title = soup.title.text.strip()

        for link in soup.select('div.maincont a')+soup.select('tr td table tr td center b a'):
            if link['href'].startswith('http') and \
                    not link['href'].startswith(tuple([self.BASE_URL] + self.OTHER_URLS)):
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=link['href'],
                                         link_title=link.text,
                                         image=img,
                                         )
