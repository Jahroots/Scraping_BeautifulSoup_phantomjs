# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class PutlockerIs(SimpleScraperBase):
    BASE_URL = "http://putlocker.co"
    OTHER_URLS = ["http://putlocker.is", "http://putlocker9.com"]

    LONG_SEARCH_RESULT_KEYWORD = '2012'


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)
    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, ], **kwargs)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/search.php?q={}'.format(search_term)

    def _fetch_no_results_text(self):
        return  "Sorry, we couldn't find the movie that you were looking for"

    def _fetch_next_button(self, soup):
            link = soup.find('a', text='Next')
            self.log.debug('-----------------')
            return link['href'] if link else None

    def _parse_search_result_page(self, soup):

        results = soup.select('table.table td a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()


        for result in results:

            if result and result.href:
                self.submit_search_result(link_title=result.text,
                                      link_url=result.href)

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        link = soup.select_one('a[rel="nofollow"]')
        if soup.select_one('h1'):
            season, episode = self.util.extract_season_episode(soup.select_one('h1').text)

        if link:
            self.submit_parse_result(index_page_title= self.util.get_page_title(soup),
                                 link_url=link.href,
                                 link_title=link.text,
                                 series_season=season,
                                 series_episode=episode)

