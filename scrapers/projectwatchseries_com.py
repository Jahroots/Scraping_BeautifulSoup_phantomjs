from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperFetchException, ScraperParseException
import re

class ProjectWatchSeries(ScraperBase):
    BASE_URL = 'http://projectwatchseries.com'

    #No Pagination found
    SINGLE_RESULTS_PAGE = True

    #Standard set up
    def setup(self):
        raise NotImplementedError('Deprecated. The resource you are looking for has been removed')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)

        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.proxy_region = 'eng'
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def search(self, search_term, media_type, **extra):

        response = self.post(
            self.BASE_URL + '/search.php',
            data={
                'searchText': search_term,
                'md': 'all',
                'submit': 'Search'
            }
        )

        soup = self.make_soup(response.text)
        self._parse_search_results(soup)

    def _parse_search_results(self, soup):

        #check if a search returns board results
        board_results = soup.select('td.mnlcategorylist a')

        if not board_results or len(board_results) == 0:
            return self.submit_search_no_results()

        #show board can have several season
        for board_result in board_results:
            soup = self.get_soup(self.BASE_URL + '/' + board_result['href'])
            seasons = soup.select('td.mnlcategorylist a')

            if not seasons or len(seasons) == 0:
                return self.submit_search_no_results()

            for season in seasons:

                #for each season we need to get the chapters they load with js only
                self.log.debug('getting from ' + season['href'] )
                self.webdriver().get(season['href'])
                soup = self.make_soup(self.webdriver().page_source)
                chapters = soup.select('a[href*="/videos/"]')

                for chapter in chapters:
                    self.submit_search_result(
                        link_url = chapter['href'],
                        link_title = chapter.text
                    )

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        scripts = soup.find('script', text= re.compile(r'codVideo'))
        for script in scripts:
            self.log.debug(script.text)
        #for soup in self.soup_each([parse_url, ]):
        #    self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        results = soup.select('object[type="application/x-shockwave-flash"]')
        if not results:
            results = soup.select('#hmovie')

        self.log.debug(results)
        for result in results:
            self.submit_parse_result(
                                     index_page_title=soup.title.text.strip(),
                                     link_url=result['src'],
                                     link_title=result.text
                                     )