# coding=utf-8

from sandcrawler.scraper import ScraperBase, ScraperParseException
from sandcrawler.scraper import SimpleScraperBase, AntiCaptchaMixin, CachedCookieSessionsMixin
from sandcrawler.scraper.caching import cacheable


class Compucaltive(AntiCaptchaMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'https://www.compucalitv.com'
    OTHER_URLS = ['http://www.compucalitv.com', 'http://compupaste.com', 'http://compul.in']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_GAME]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    RECAPKEY = '6LedIyEUAAAAAN9QW8JrGy2J2H7bkgIqoqJ6pKZs'
    RECAPURL = 'http://compupaste.com/'

    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/{}'.format(self.util.quote(search_term))

    @cacheable()
    def _extract_link(self, url):
        self.load_session_cookies()
        soup = self.get_soup(url)
        if soup.select('div.g-recaptcha'):
            # we need to solve a recap.
            soup = self.post_soup(
                url,
                data={
                    'g-recaptcha-response': self.get_recaptcha_token()
                }
            )
            if 'Captcha incorrecto' in unicode(soup):
                raise ScraperParseException('Invalid captcha returned')
            self.save_session_cookies()
        # otherwise, dig out the actual url.
        return list(self.util.find_urls_in_text(soup.select_one('div.tab_content').text))

    def _fetch_next_button(self, soup):
        link = None
        try:
            link = soup.find('a', text=u'»')['href']
        except TypeError:
            pass
        return link if link else None

    def _parse_search_result_page(self, soup):
        blocks = soup.select('#contenidoz a')
        if not blocks:
            return self.submit_search_no_results()
        for block in blocks:
            link = block['href']
            self.submit_search_result(
                    link_url=link,
                    link_title=block['title']
                )

    def _parse_parse_page(self, soup):

        link = soup.select_one('#info a')

        index_page_title = self.util.get_page_title(soup)

        result = link['href']
        if result.startswith('http://compupaste.com'):
            for result in self._extract_link(result):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=result,
                )
        else:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=result,
            )