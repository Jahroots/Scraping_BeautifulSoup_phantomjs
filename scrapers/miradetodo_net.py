# coding=utf-8
import re, base64
from binascii import Error
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin

class MiradetodoNet(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL =  'http://miradetodo.io'
    OTHER_URLS = ['http://miradetodo.net', 'miradetodo.com.ar']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    pag = 1
    REQUIRES_WEBDRIVER=True
    WEBDRIVER_TYPE = 'phantomjs'
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    ALLOW_FETCH_EXCEPTIONS = True

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Contenido no disponible'

    def _fetch_next_button(self, soup):
        next_button = self.BASE_URL + '/page/' + str(self.pag) + '/?s=' + self.util.quote(self.search_term)
        self.pag += 1

        return next_button

    def can_fetch_next(self, *args, **kwargs):
        return self.more_results and super(self.__class__, self).can_fetch_next(*args, **kwargs)

    def search(self, search_term, media_type, **extra):
        self.pag = 2
        self.search_term = search_term
        self.more_results = True
        super(self.__class__, self).search(search_term, media_type, **extra)

    def _parse_search_result_page(self, soup):
        results = soup.select('div.peliculas div.item a')

        for result in results:
            link = result
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

        next_button_link = self._fetch_next_button(soup)
        if next_button_link and self.can_fetch_next():
            response = self.get(next_button_link, allowed_errors_codes=[404, ])
            self.log.debug(response.status_code)
            if response.status_code == 200:
                self._parse_search_results(
                    self.make_soup(response.content)
                )
            else:
                self.more_results = False

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1').text
        for link in soup.select('div.movieplay iframe[data-lazy-src]'):
            url = link['data-lazy-src']
            if url:
                soup = self.get_soup(url)
                iframe = soup.select_one('iframe')
                if iframe and iframe['src']:
                    self.log.debug(iframe['src'])
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=iframe['src'],
                        link_title=title
                    )
                else:
                    download_link = soup.select_one('a[href*="down.php"]')
                    if download_link:
                        download_link = download_link['href']
                        if 'down.php?id=' in download_link:
                            play_url = re.search('id=(.*)&', download_link)
                            if play_url:
                                movie_link = ''
                                try:
                                    movie_link = base64.decodestring(play_url.groups()[0])
                                except Error:
                                    pass
                                if not movie_link:
                                    try:
                                        movie_link = base64.decodestring(play_url.groups()[0]+'=')
                                    except Error:
                                        pass
                                if movie_link:
                                    self.submit_parse_result(
                                        index_page_title=index_page_title,
                                        link_url=movie_link,
                                        link_title=title
                                    )

