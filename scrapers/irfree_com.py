# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin


class IrFree(CloudFlareDDOSProtectionMixin, ScraperBase):
    BASE_URL = 'https://irfree.com'
    LONG_SEARCH_RESULT_KEYWORD = '2016'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ]:  # + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

        # OpenSearchMixin advanced search settings
        self.bunch_size = 400
        self.media_type_to_category = 'film 14, tv 0'
        # self.encode_search_term_to = 'utf256'
        self.showposts = 0

    def _do_search(self, search_term, page=1, result_from = 1):
        return self.post_soup(
            self.BASE_URL+'/index.php?do=search',
            data={
                'do':'search','subaction':'search','story':self.util.quote(search_term), 'search_start':'{}'.format(page), 'full_search':'0', 'result_from':result_from
            }
        )

    def search(self, search_term, media_type, **extra):
        first_page = self._do_search(search_term)
        if unicode(first_page).find(u'Unfortunately, site search yielded no results.') >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(first_page)
        page = 1
        while self.can_fetch_next():
            page += 1
            result_from = page*10+1
            soup = self._do_search(
                search_term,
                page, result_from
            )
            if not self._parse_search_result_page(soup):
                return

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None

    def _fetch_no_results_text(self):
        return u'Unfortunately, site search yielded no results.'

    def _parse_search_result_page(self, soup):
        for result in soup.select("h3.panel-title > a"):
            self.submit_search_result(link_title=result.text,
                                      link_url=result.get('href'))

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        title = soup.title.text[:-9]
        series_season, series_episode = self.util.extract_season_episode(title)
        for link in soup.select('.textinfobox.clearfix a'):
            try:
                rel = link['rel']
            except KeyError:
                continue
            if 'external' in rel:
                if 'imdb.com' not in link['href'] and 'fastpic' not in link['href'] and 'tv.com' not in link['href']:
                    self.submit_parse_result(
                        index_page_title=self.util.get_page_title(soup),
                        link_title=title,
                        link_url=link['href'],
                        series_season=series_season,
                        series_episode=series_episode,
                        )

        for lnk in soup.select('.quote a'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=lnk.href,
                link_title=title,
                series_season=series_season,
                series_episode=series_episode,
            )
        for lnk in soup.select('pre center a[target="_blank"]'):
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=lnk.href,
                link_title=title,
                series_season=series_season,
                series_episode=series_episode,
            )
