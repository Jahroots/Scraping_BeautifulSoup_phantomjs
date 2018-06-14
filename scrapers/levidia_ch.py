# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, \
    CacheableParseResultsMixin, ScraperFetchException
from sandcrawler.scraper.caching import cacheable

class LevidiaCh(CacheableParseResultsMixin, SimpleScraperBase):
    BASE_URL = 'http://www.levidia.ch'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    REQUIRES_WEBDRIVER = ('parse', )
    WEBDRIVER_TYPE = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
        url = '{base_url}/search.php?submit=&q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)
        if media_type == ScraperBase.MEDIA_TYPE_TV:
            url += '&v=episodes'
        elif media_type == ScraperBase.MEDIA_TYPE_FILM:
            url += '&v=movies'
        return url

    def _fetch_no_results_text(self):
        return u'Nothing Found'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text='Next »')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('ul.mfeed li.mlist'):
            link = result.select_one('a')
            url = link.href
            if url.startswith('tv-show'):
                series_soup = self.get_soup('{}/{}'.format(self.BASE_URL, url))
                for link in series_soup.select('ul.mfeed li.links a'):
                    self.submit_search_result(
                        link_url='{}/{}'.format(self.BASE_URL, link.href),
                        link_title=link.text,
                        image=self.util.find_image_src_or_none(result, 'img'),
                    )
            else:
                self.submit_search_result(
                    link_url='{}/{}'.format(self.BASE_URL, link.href),
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def parse(self, parse_url, **extra):
        wd = self.webdriver()
        wd.get(parse_url)
        for cookie in wd.get_cookies():
            print(cookie)
            self._http_session.cookies.set(
                cookie['name'],
                cookie['value'],
                domain=cookie['domain']
            )

        soup = self.make_soup(
            wd.page_source
        )
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('ul.mfeed li a'):
            url = self.get_redirect_location(link.href)
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )
