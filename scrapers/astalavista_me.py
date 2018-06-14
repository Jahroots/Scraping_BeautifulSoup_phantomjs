# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class Astalavista_me(SimpleScraperBase):
    BASE_URL = 'http://astalavista.me'
    OTHER_URLS = []

    LONG_SEARCH_RESULT_KEYWORD = 'dvdscr'

    def setup(self):
        raise NotImplementedError('Site no longer available.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        data = dict(
            search_app='forums', search_term=search_term, andor_type='and', search_content='titles', search_tags='',
            search_author='', search_date_start='', search_date_end='')
        data.update({
            'search_app_filters[core][sortKey]': 'date',
            'search_app_filters[core][sortDir]': '0',
            'search_app_filters[forums][noPreview]': '1',
            'search_app_filters[forums][pCount]': '',
            'search_app_filters[forums][pViews]': '',
            'search_app_filters[forums][sortKey]': 'date',
            'search_app_filters[forums][sortDir]': 0,
            'submit': 'Search Now'})

        soup = self.post_soup(self.BASE_URL + '/index.php?app=core&module=search&section=search&do=search&fromsearch=1',
                              data=data)
        self._parse_search_results(soup)

    def _fetch_no_results_text(self):
        return 'No posts found'

    def _fetch_next_button(self, soup):
        link = soup.select_one('.next a')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('td h4 a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('.ipsType_pagetitle').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('.prettyprint'):
            for url in self.util.find_urls_in_text(link.text):
                self.submit_parse_result(
                    index_page_title=soup.title.text.strip(),
                    link_url=url,
                    link_title=title,
                    series_season=season,
                    series_episode=episode
                )
