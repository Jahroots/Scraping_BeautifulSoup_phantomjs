# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, AntiCaptchaMixin, ScraperParseException
from sandcrawler.scraper.caching import cache
from redis_cache.rediscache import CacheMissException
from sandcrawler.scraper.caching import cacheable

class GoldeselTo(SimpleScraperBase, AntiCaptchaMixin):
    BASE_URL = 'http://goldesel.to'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'deu'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    RECAPKEY = '6LcDZAgTAAAAAFK3shKJrBbtT869bWKOX42CzNSa'

    cache_key = 'GoldeselTo__PHPSESSID'

    def setup(self):
        raise NotImplementedError('Involves complex captures to download')

    @cacheable()
    def _get_cookie(self):
        try:
            return cache.get_pickle(self.cache_key)
        except (KeyError, CacheMissException):
            pass

        self.post(
            self.BASE_URL + '/suche/man',
            data = {
                'g-recaptcha-response': self.get_recaptcha_token()
            }
        )

        cookie_val = self.http_session().cookies['PHPSESSID']
        cache.store_pickle(self.cache_key, cookie_val)

        return cookie_val


    def _load_cookies(self):
        self._http_session.cookies.set(
            'PHPSESSID',
            self._get_cookie(),
            domain='goldesel.to'
        )


    def search(self, search_term, media_type, **extra):
        category = {
            ScraperBase.MEDIA_TYPE_FILM: 3,
            ScraperBase.MEDIA_TYPE_GAME: 2,
            ScraperBase.MEDIA_TYPE_TV: 4,
            ScraperBase.MEDIA_TYPE_BOOK: 7,
        }
        category_id = category.get(media_type, '')
        self._load_cookies()
        tries = 0
        step = '{};{};0'.format(self.util.quote(search_term), category_id)
        while self.can_fetch_next():
            soup = self.post_soup(
                self.BASE_URL + '/res/suche',
                data={
                    'Step': step,
                },
                headers={

                }
            )
            if not soup:
                if tries > 2:
                    raise ScraperParseException('Could not get search response after 2 tries.')
                tries += 1
                cache.invalidate(self.cache_key)
                self._load_cookies()
            else:
                for link in soup.select('a'):
                    text_block = link.select_one('div.tle')
                    link_title = None
                    if text_block:
                        link_title = text_block.text
                    self.submit_parse_result(
                        link_url=self.BASE_URL + '/' + link.href,
                        link_title=link_title,
                        image=self.util.find_image_src_or_none(link, 'img.lazy')
                    )




    def _parse_search_result_page(self, soup):
        for result in soup.select('ul.rls_table>a'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select(' TODO '):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.title,
            )
