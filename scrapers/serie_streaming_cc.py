# coding=utf-8
import base64
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, ScraperBase, SimpleScraperBase
from sandcrawler.scraper.caching import cacheable

class SerieStreamingCc(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://serie-streaming.ws'
    OTHERS_URLS = ['https://www.serie-streaming.cc', 'http://ww1.serie-streaming.cc', 'http://serie-streaming.ws', 'http://serie-streaming.cc', 'http://serie-streaming.co']
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'friends'
    OTHER_URLS = []
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'

    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def __buildlookup(self):
        lookup = {}
        for mainsoup in self.soup_each([self.BASE_URL]):
            for serial_link in mainsoup.select('div.list-group a'):
                lookup[serial_link.text.lower().strip() + ' ' + serial_link.text.strip()] = serial_link.href.strip()
        return lookup

    def search(self, search_term, media_type, **extra):
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)
        any_results = False
        submitted = set()
        for term, page in lookup.items():
            if search_regex.match(term):
                series_soup = self.get_soup(self.BASE_URL + page)
                series_links = series_soup.find_all('button', 'btn btn-primary ')
                for ser_link in series_links:
                    series_link = ser_link.find_previous('a').href
                    ep_soup = self.get_soup(self.BASE_URL + series_link)
                    ep_links = ep_soup.find_all('button', 'btn btn-primary')
                    for ep_link in ep_links:
                        episode_link = ep_link.find_previous('a').href
                        episode_s = self.get_soup(self.BASE_URL + episode_link)
                        for v in episode_s.select('div a[href*="streaming.html"]'):
                            url = self.BASE_URL + v['href'].strip()
                            if 'episode' not in url:
                                # Skip other season links
                                continue
                            if url not in submitted:
                                self.submit_search_result(
                                    link_url=url,
                                    link_title=term,
                                )
                                submitted.add(url)

                any_results = True
        if not any_results:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)

    @cacheable()
    def _follow_url(self, url):
        soup = self.get_soup(url)
        link = soup.select_one('a[class*="btn btn-success"]')
        if link:
            return link.href
        return self.util.extract_meta_refresh(soup)


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        for link in soup.select('a.iframelink'):
            url = self._follow_url(
                self.BASE_URL + link['href']
            )
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=title.text,
                series_season=series_season,
                series_episode=series_episode,
            )