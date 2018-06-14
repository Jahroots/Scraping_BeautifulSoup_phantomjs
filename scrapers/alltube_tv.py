# coding=utf-8


import base64
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, ScraperBase


class AlltubeTv(CloudFlareDDOSProtectionMixin, ScraperBase):
    BASE_URL = 'http://alltube.tv'
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'pol'
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]
    TRELLO_ID = 'TM21SL7D'

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/szukaj',
                data={
                    'search': search_term,
                }
            )
        )

    def _parse_search_results(self, soup):
        self.block = False
        for result in soup.select('div.container-fluid div.item-block a'):
            title = result.find('h3').text
            link = result['href']
            self.submit_search_result(
                link_url=link,
                link_title=title,
            )
            self.block = True
        if not self.block:
            return self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            for series_links in soup.select('li.episode a'):
                series_soup = self.get_soup(series_links['href'])
                for filmki_iframe in series_soup.select('div#links-container a.watch'):
                    filmki_link = self.get_soup(base64.decodestring(filmki_iframe['data-iframe'])).find('iframe')['src']
                    if 'http' not in filmki_link:
                        filmki_link = 'http:' + filmki_link
                    filmki_title = soup.find('h2', 'headline')
                    if filmki_title:
                        filmki_title = filmki_title.text.strip()
                        season, episode = self.util.extract_season_episode(filmki_title)
                        self.submit_parse_result(index_page_title=self.util.get_page_title(series_soup),
                                                 link_url=filmki_link,
                                                 link_title=filmki_title,
                                                 series_season=season,
                                                 series_episode=episode,
                                                 )
            for filmki_iframe in soup.select('div#links-container a.watch'):
                filmki_link = self.get_soup(base64.decodestring(filmki_iframe['data-iframe'])).find('iframe')['src']
                if 'http' not in filmki_link:
                    filmki_link = 'http:'+filmki_link
                filmki_title = soup.find('h2', 'headline')
                if filmki_title:
                    filmki_title = filmki_title.text
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=filmki_link,
                                         link_title=filmki_title
                                         )

