# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase, OpenSearchMixin


class ThreeDsbs4u(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://3dsbs4u.com'
    OTHER_URLS = ['http://3dsbs4u.com']
    USER_AGENT_MOBILE = False
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    SEARCH_TERM = ''
    PAGE = 1
    RESULTS = 0

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[520], **kwargs)

    def _parse_search_result_page(self, soup):

        results = soup.select('#dle-content td.stext a img')
        self.log.warning(len(results))
        if (not results or len(results) == 0) and self.PAGE == 1:
            return self.submit_search_no_results()

        self.PAGE += 1
        for result in results:
            if 'extremetracking' in result.parent.href:
                continue
            self.submit_search_result(
                link_url=result.parent['href'],
                link_title=result.text
            )


    def _parse_parse_page(self, soup):
        title = soup.select_one('.ntitle > a > b')
        if title:
            title = title.text.strip()
            season, episode = self.util.extract_season_episode(title)
        else:
            season = episode = None

        for lnk in soup.select('.quote a'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=lnk.href,
                link_title=title,
                series_season=season,
                series_episode=episode,
                )
