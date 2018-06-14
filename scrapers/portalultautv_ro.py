# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class PortalultautvRo(SimpleScraperBase):
    BASE_URL = 'https://www.portalultautv.com'
    OTHER_URLS = ['http://www.portalultautv.com', 'http://portalultautv.ro']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    REQUIRES_WEBDRIVER = ('parse', )
    WEBDRIVER_TYPE = 'phantomjs'

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    TRELLO_ID = 'DFC83opL'

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Din pacate nu a fost nimic gasit'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('div.nav-previous a')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('div.main-article div.feat-thumb-holder'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link['title'],
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def parse(self, parse_url, **extra):

        # Javascript encryption.
        self.webdriver().get(parse_url)
        soup = self.make_soup(self.webdriver().page_source)

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        for link in soup.select('div.entry-content iframe'):
            if 'youtube' in link['src']:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link['src'],
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

