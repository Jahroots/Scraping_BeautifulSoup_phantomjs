# coding=utf-8
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FilmoljupciCom(SimpleScraperBase):
    BASE_URL = 'http://filmonet.com'
    OTHER_URLS = ['http://filmoljupci.com', 'https://filmoljupci.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cro'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    REQUIRES_WEBDRIVER = ('parse', )
    WEBDRIVER_TYPE = 'phantomjs'


    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search/?q={search_term}'.format(base_url=self.BASE_URL, search_term=self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Rezultati 0-0'

    def _fetch_next_button(self, soup):
        next_button = None
        try:
            next_button = soup.find('span', 'pagesBlockuz1').find('span', text=u'»').find_previous()
        except AttributeError:
            pass
        if next_button:
            return 'http:'+next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.eTitle'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        # Javascript obfuscated links..
        self.webdriver().get(parse_url)
        soup = self.make_soup(self.webdriver().page_source)

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.eTitle')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        results = soup.select('td.eText a[target="_blank"]')
        for result in results:
            if result.href == '#':
                continue

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url= result.href,
                link_title=title.text,
                series_season=series_season,
                series_episode=series_episode,
            )
