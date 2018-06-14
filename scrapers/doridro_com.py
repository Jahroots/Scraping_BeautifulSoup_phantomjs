# coding=utf-8

from sandcrawler.scraper import ScraperAuthException
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class DoridroCom(SimpleScraperBase):
    BASE_URL = 'http://doridro.com'

    USERNAME = 'Liare1938'
    PASSWORD = 'bi3Aushoh4'
    EMAIL = 'RobertCNordman@dayrep.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _login(self):
        response = self.post(
            self.BASE_URL + '/forum/ucp.php?mode=login',
            data={'username': self.USERNAME,
                  'password': self.PASSWORD,
                  'login': 'Login',
                  'redirect': 'index.php',
                  }
        )
        if response.content.find('You have specified an incorrect username') >= 0:
            raise ScraperAuthException("Invalid username/password")

    def search(self, search_term, media_type, **extra):
        self._login()
        return super(DoridroCom, self).search(search_term, media_type, **extra)

    def _fetch_no_results_text(self):
        return 'No suitable matches were found.'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/forum/search.php?terms=all&author=&fid' \
                               '%5B%5D=137&sc=1&sf=titleonly&sr=posts&sk=t&sd=d&st=0&ch=300&t=0&' \
                               'submit=Search&keywords=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        if link:
            return self.BASE_URL + '/forum' + link['href'][1:]
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.well div.pull-left h4 a'):
            self.submit_search_result(
                link_url=self.BASE_URL + '/forum' + result['href'][1:],
                link_title=result.text,
            )

    def parse(self, parse_url, **extra):
        self._login()
        return super(DoridroCom, self).parse(parse_url, **extra)

    def _parse_parse_page(self, soup):
        links = set()
        link_titles = {}
        title = soup.select_one('.side-segment h3').text

        for link in soup.select('div.content a'):
            if link['href'].startswith('http'):
                links.add(link['href'])
                link_titles[link['href']] = link.text

        for link in self.util.find_urls_in_text(str(soup.select('div.content')), skip_images=True):
            links.add(link)

        for link in links:
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link,
                                     link_title=link_titles.get(link) or title,
                                     )
