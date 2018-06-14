# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin

class LovelystreamWs(CachedCookieSessionsMixin, CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://www.lovelystream.ws'
    OTHER_URLS = ['https://www.lovelystream.ws','http://www.lovelystream.ws']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [  ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True
    WEBDRIVER_TYPE = 'phantomjs'
    REQUIRES_WEBDRIVER = True
    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def _fetch_no_results_text(self):
        return None#u'Désolé, mais rien ne correspond à votre critère de recherche'

    def _fetch_next_button(self, soup):
        return None

    def search(self, search_term, media_type, **extra):
        self.webdriver().get(self.BASE_URL + '/?s={}'.format(search_term))
        soup = self.make_soup(self.webdriver().page_source)
        for cookie in self.webdriver().get_cookies():
            self.http_session().cookies.set(cookie['name'], cookie['value'])
        self.save_session_cookies()
        self._parse_search_result_page(soup)
    def _parse_search_result_page(self, soup):
        results = soup.select('article div.entry-summary')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result.select_one('a.bt-voir')
            soup = self.get_soup(link.href)

            seasons = soup.select('li[class*="cat-item"] a')

            for season in seasons:
                soup = self.get_soup(season.href)
                chapters = soup.select('article div.entry-summary a.bt-voir')
                for chapter in chapters:
                    self.submit_search_result(
                        link_url=chapter.href,
                        link_title=chapter.text,
                        image=self.util.find_image_src_or_none(result, 'img'),
                    )

    def parse(self, parse_url, **extra):
        self.load_session_cookies()
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1.entry-title-single').text
        episode, season = self.util.extract_season_episode(title)

        for link in soup.select('article iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=link.text,
                episode = episode,
                season = season
            )
