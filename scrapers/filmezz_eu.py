# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, AntiCaptchaImageMixin
from sandcrawler.scraper.caching import cacheable
import re


class FilmezzEu(AntiCaptchaImageMixin, SimpleScraperBase):
    BASE_URL = 'http://filmezz.eu'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP,]
    LANGUAGE = 'hun'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    USER_NAME = 'Paides'
    PASSWORD = 'de9ooY5ooyae'
    EMAIL = 'amandajrobertson@rhyta.com'

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404, ], **kwargs)

    def _fetch_no_results_text(self):
        return u'A megadott feltételekkel nincs találat'

    def _fetch_search_url(self, search_term, media_type=None):
        self.page = 1
        self.search_term = search_term
        return self.BASE_URL + u'/kereses.php?s={}'.format(self.util.quote(search_term.decode('utf8')))

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)

        self.page += 1
        next_button_link = soup.find(
            'a', text=self.page
        )
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    u'{}/{}'.format(self.BASE_URL, next_button_link.href),
                )
            )

    def _parse_search_result_page(self, soup):

        for link in soup.select('ul[class="row list-unstyled movie-list"] a'):
            if 'film.php' in link.href:
                title = soup.select_one('.title').text.strip()
                self.submit_search_result(
                        link_title=title,
                        link_url=self.BASE_URL + '/' + link.href,
                        image = self.util.find_image_src_or_none(link, 'img')
                    )


    @cacheable()
    def _get_link(self, url):
        return self.get(url).url

    def _parse_parse_page(self, soup):
        links = soup.select('a[class="url-btn play"]')
        for link in links:
            asset_id = re.search('id(.*)', link.href)
            asset_id = asset_id.group(1).split('%3D' or '=') if asset_id else None
            if asset_id:
                url = self.BASE_URL + '/link_to.php?id=' + asset_id[1]
                self.log.debug(url)
                try:

                    key = self.solve_captcha(self.BASE_URL + '/captchaimg.php')

                    soup = self.post_soup(url, data={'captcha': key,
                                                     'submit': 'They'})

                    index_page_title = self.util.get_page_title(soup)

                    iframe = soup.select_one('iframe[allowfullscreen]')
                    if iframe and iframe.has_attr('src'):
                        self.submit_parse_result(index_page_title=index_page_title,
                                                 link_url=iframe['src'],
                                                 )
                    else:
                        self.submit_parse_result(index_page_title=index_page_title,
                                                 link_url=url,
                                                 )

                except Exception as e:
                    self.log.warning(e)

