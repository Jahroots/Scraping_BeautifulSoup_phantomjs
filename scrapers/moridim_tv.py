# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin

class MoridimTv(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://moridim.tv'
    OTHER_URLS = ['http://moridim.tv']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'heb'
    REQUIRES_WEBDRIVER = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    ALLOW_FETCH_EXCEPTIONS = True

    def setup(self):
        super(self.__class__, self).setup()
        self.webdriver_type = 'phantomjs'

    def _do_search(self, search_term, page=0):
        return self.post_soup(
            self.BASE_URL + '/ajax/search.php',
            data={'q': self.util.quote(search_term), 'index': '{}'.format(page),'limit':'10'}
        )

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        first_page = self._do_search(search_term)
        if unicode(first_page).find(u'אין תוצאות') >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(first_page)
        page = 1
        while self.can_fetch_next():
            page += 1
            soup = self._do_search(
                search_term,
                page
            )
            if not self._parse_search_result_page(soup):
                break

    def _parse_search_result_page(self, soup):
        found = False
        for result in soup.select('div.download'):
            link = result.select_one('a')
            link_url = u'{}/{}'.format(
                self.BASE_URL,
                link.href,
            )

            self.submit_search_result(
                link_url=link_url,
                link_title=link.text,
                image= self.BASE_URL + self.util.find_image_src_or_none(result, 'img'),
            )
            found = True

        return found


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div#downloadsReleases a.button'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
