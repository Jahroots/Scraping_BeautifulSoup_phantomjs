# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, AntiCaptchaMixin, CachedCookieSessionsMixin
import re
from sandcrawler.scraper.caching import cacheable


class VeziOnlineCom(AntiCaptchaMixin, CachedCookieSessionsMixin,SimpleScraperBase):
    BASE_URL = 'https://vezi-online.org'
    OTHER_URLS = ['https://vezi-online.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    RECAPKEY = '6LeYwj4UAAAAAAXgG3tgke-eCvpqdfulJXIkTpkV'

    USERNAME = 'Wasterem1933'
    PASSWORD = 'thai2ooBepo'
    EMAIL = 'patriciaiwhitaker@jourrapide.com'


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Ne pare rau, nu am gasit nici un rezultat pentru cautarea dumneavoastra'

    def get(self, url, **kwargs):
        return super(VeziOnlineCom, self).get(url, allowed_errors_codes=[404], **kwargs)

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('#nextpagination')
        if next_button:
            return next_button.parent.href
        return None

    def _login(self):
        soup = self.post_soup(self.BASE_URL + '/wp-login.php' , data = {'log': self.USERNAME, 'pwd' : self.PASSWORD, 'redirect_to' : self.BASE_URL + "/"})
        self.log.debug(soup.select('div.gravatar'))
        self.save_session_cookies()

    def search(self, search_term, media_type, **extra):
        self._login()
        soup = self.get_soup(self._fetch_search_url(search_term, media_type))
        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        for result in soup.select('div[class="result-item"] article div.title'):

            link = result.select_one('a')
            if link:
                if 'serial' in link.href:
                    soup = self.get_soup(link.href)
                    episodes = soup.select('ul.episodios div.episodiotitle a')
                    for episode in episodes:
                        self.submit_search_result(
                            link_url=episode.href,
                            link_title=episode.text,
                            image=self.util.find_image_src_or_none(result, 'img'),
                        )
                else:
                    self.submit_search_result(
                        link_url=link.href,
                        link_title=link.text,
                        image=self.util.find_image_src_or_none(result, 'img'),
                    )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)



    def parse(self, parse_url, **extra):
        self.load_session_cookies()
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1.entry-title')
        if title and title.text:
            title = title.text

            # Dig out the page item.
        id = re.search(
                'data: {id: (\d+)}',
                unicode(soup)
        ).group(1)
        self.log.warning(id)
        soup = self.post_soup(self.BASE_URL + '/sursa/show.php', data={'id': id})


        if 'recaptcha' in unicode(soup):
            self._resolve_captcha()
            soup = self.post_soup(self.BASE_URL + '/sursa/show.php', data={'id': id})

        iframes = soup.select('iframe')
        for iframe in iframes:

            self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe['src'],
                    link_title=title
            )

    @cacheable()
    def _resolve_captcha(self):

        self.post_soup(
                self.BASE_URL,
                data={
                    'g-recaptcha-response': self.get_recaptcha_token()
                }
            )

        self.save_session_cookies()

