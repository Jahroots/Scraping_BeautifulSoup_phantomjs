# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class DLwarez(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://dlwarez.in'
    OTHER_URLS = ['http://dlwarez.in', 'http://www.dlwarez.in', ]
    USER_AGENT_MOBILE = False

    # LONG_SEARCH_RESULT_KEYWORD = 'жизнь'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 15
        self.media_type_to_category = 'film 2, tv 25'
        self._request_connect_timeout = 900
        self._request_response_timeout = 900
        # self.encode_search_term_to = 'cp1251'
        # self.showposts = 0

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _fetch_next_button(self, soup):
        return None

    def _do_search(self, search_term, page=1):
        result_from = page*10-9
        return self.post_soup(
            self.BASE_URL+'/index.php?do=search',
            data={
                'do':'search',
                'subaction':'search',
                'search_start':page,'full_search':0,
                'result_from':result_from, 'story': self.util.quote(search_term),
            }
        )


    def search(self, search_term, media_type, **extra):
        first_page = self._do_search(search_term)
        if unicode(first_page).find(u'Unfortunately, site search yielded no results') >= 0:
           return self.submit_search_no_results()
        self._parse_search_result_page(first_page)
        page = 0
        while self.can_fetch_next():
            page += 1
            soup = self._do_search(
                search_term,
                page
            )
            if not self._parse_search_result_page(soup):
                return

    def _parse_search_result_page(self, soup):
        results = soup.select('.zag a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for link in results:
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )


    def _parse_parse_page(self, soup):
        try:
            title = soup.select_one('.zag a')
            series_season, series_episode =('', '')
            if title:
                title=title.text
                series_season, series_episode = self.util.extract_season_episode(title)

            for lnk in soup.select('.quote a'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=lnk.href,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

        except Exception as e:
            self.log.exception(e)
