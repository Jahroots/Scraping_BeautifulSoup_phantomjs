# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class GledajSa(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://www.gledajsaprevodom.club'
    OTHER_URLS = ['https://www.gledajsaprevodom.info', 'https://www.gledajsaprevodom.net', 'http://www.gledajsaprevodom.com']
    USERNAME = 'Giaten65'
    PASSWORD = 'meL1ooli'
    EMAIL = 'jessieagregg@jourrapide.com'
    LONG_SEARCH_RESULT_KEYWORD = 'the'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'ser'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'
        self._request_connect_timeout = 500
        self._request_response_timeout = 600

    LONG_SEARCH_RESULT_KEYWORD = 'the'

    #The reason to use webdriver for this scraper is the 30 maximum redirects.

    def _login(self):
        self.post(self.BASE_URL, data = {'username': self.USERNAME, 'password' : self.PASSWORD, 'action' : 'login'})

    def search(self, search_term, media_type, **extra):
        self._login()
        soup = self.get_soup(self._fetch_search_url(search_term, media_type))

        self._parse_search_result_page(soup)


    def get(self, url, **kwargs):
        return super(GledajSa, self).get(url, allowed_errors_codes=[503], **kwargs)

    def _fetch_no_results_text(self):
        return u'Na žalost, nismo pronašli ni jedan termin u pretrazi'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?menu=search&query=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.item a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            #if the search is film
            if 'film' in result['href']:
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result.text,
                    image = self.util.find_image_src_or_none(result, 'img')
                )
            else:
                #look up for seasons and episodes
                soup = self.get_soup(result['href'])
                seasons = soup.select('h5.tv_episode_item a.link')

                for season in seasons:
                    self.submit_search_result(
                        link_url=season['href'],
                        link_title=result['title'],
                        image=self.util.find_image_src_or_none(result, 'img')
                    )



    def parse(self, parse_url, **extra):
        self._login()
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.find_all('a', text = u'Gledaj Besplatno Online'):
            soup = self.get_soup(link.href)
            videos = soup.select('iframe')
            for video in videos:
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=video['src'],
                    link_title=title,
                    series_season=season,
                    series_episode=episode
                )
