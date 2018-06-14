# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import json, re
from sandcrawler.scraper.caching import cacheable

class Onlinedizi1Co(SimpleScraperBase):
    BASE_URL = 'http://onlinedizi.com'
    OTHER_URLS = ['http://onlinedizi1.co']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    LONG_SEARCH_RESULT_KEYWORD = 'The'

    def get(self, url, **kwargs):
        return super(Onlinedizi1Co, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    @cacheable()
    def __build_section_lookup(self, soup):

        lookup = {}
        for link in soup.select('ul[class="all-list posts-list"] div.b-video a'):
            lookup[link.text.strip()] = link['href']
        next_link = soup.select_one('div.v-pagination a[aria-label="Next"]')
        if next_link:
            lookup.update(
                self.__build_section_lookup(self.get_soup(next_link['href']))
            )
        return lookup

    @cacheable()
    def __buildlookup(self):
        # Build a dict of show name -> url for the whole site.
        lookup = {}
        for mainsoup in self.soup_each([self.BASE_URL, ]):
            lookup.update(self.__build_section_lookup(mainsoup))
        return lookup


    def search(self, search_term, media_type, **extra):
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)

        any_results = False
        for term, page in lookup.items():
            self.log.debug(term)
            if search_regex.match(term):
                self.submit_search_result(
                    link_url=page,
                    link_title=term,
                )
                any_results = True

        if not any_results:
            self.submit_search_no_results()




    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        series_season, series_episode = self.util.extract_season_episode(index_page_title)
        links_src = soup.select('ul.dropdown-menu a')
        for link_src in links_src:
            link_soup = self.get_soup(link_src['href'])
            iframe = link_soup.select_one('div.player iframe')
            if iframe:
                iframe_src = iframe['wpfc-data-original-src']
                if "http" not in iframe_src:
                    iframe_src = 'http:' + iframe_src
                frame1_soup = self.get_soup(
                    iframe_src,
                    headers={
                        'Referer': soup._url,
                    }
                )
                iframe2 = frame1_soup.select_one('iframe')
                if iframe2:
                    iframe2_src = iframe2['src']
                    if "http" not in iframe2_src:
                        iframe2_src = 'http:' + iframe2_src
                    if self.BASE_URL not in iframe2_src:
                        link_url = iframe2_src
                    else:
                        link_url = self.get_redirect_location(iframe2_src)
                    if "http" not in link_url:
                        link_url = 'http:' + link_url
                    if 'domain=' in link_url:
                        link_url = link_url.split('domain=')[-1]
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link_url,
                        link_title=link_url,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

