# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.extras import CloudFlareDDOSProtectionMixin, CacheableParseResultsMixin
from sandcrawler.scraper.caching import cacheable


class Streamzzz(CacheableParseResultsMixin, CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://streamzzz.online'
    OTHER_URLS = ['http://streamzzz.com', ]
    LANGUAGE = 'fra'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    MEDIA_TYPES = [
        ScraperBase.MEDIA_TYPE_TV,
    ]
    URL_TYPES = [
        ScraperBase.URL_TYPE_SEARCH,
        ScraperBase.URL_TYPE_LISTING
    ]
    
    def setup(self):
        super(Streamzzz, self).setup()
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
        return u'{}/?s={}'.format(self.BASE_URL, search_term)

    def _fetch_next_button(self, soup):
        # Find the 'current' page.
        pagination = soup.select_one('div.pagination')
        if not pagination:
            return None
        current = pagination.select_one('span.current')
        if not current:
            return None
        for sibling in current.next_siblings:
            if sibling.name == 'a':
                return sibling['href']
        return None

    def _fetch_no_results_text(self):
        return u'Aucun résultat pour montrer avec'

    def _parse_search_result_page(self, soup):

        for series_link in soup.select('div.result-item div.details div.title a'):
            series_soup = self.get_soup(series_link.href)
            for link in series_soup.select('ul.episodios div.episodiotitle a'):
                self.submit_search_result(
                    link_title=link.text,
                    link_url=link.href,
                )


    @cacheable()
    def _follow_link(self, link):
        soup = self.get_soup(link)
        link = soup.select_one('div.boton.reloading a')
        return link and link.href or None

    def _parse_parse_page(self, soup):
        index_title = self.util.get_page_title(soup)
        series_season, series_episode = self.util.extract_season_episode(index_title)
        for link in soup.select('div.links_table a.link_a'):
            self.submit_parse_result(
                index_page_title=index_title,
                link_url=self._follow_link(link['href']),
                link_text=link.text,
                series_season=series_season,
                series_episode=series_episode,
                )
