# coding=utf-8
from base64 import decodestring

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperParseException, ScraperFetchException
from sandcrawler.scraper import SimpleScraperBase, AntiCaptchaMixin, CachedCookieSessionsMixin
import re
from sandcrawler.scraper.caching import cacheable

class Movie25Ag(AntiCaptchaMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'http://5movies.to'
    OTHER_URLS = [
        'http://tinklepad.is',
        'http://movie25.ph',
        'http://www.movie25.ag',
        'http://movie25.hk',
        'http://www.movie25.hk',
        'http://tinklepad.ag'
    ]
    LANGUAGE = 'eng'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    MEDIA_TYPES = [
        ScraperBase.MEDIA_TYPE_TV,
    ]
    URL_TYPES = [
        ScraperBase.URL_TYPE_SEARCH,
        ScraperBase.URL_TYPE_LISTING
    ]

    USER_AGENT_MOBILE = False
    RECAPKEY = '6LebzyEUAAAAAM_9LiY9_bv4owJN9Nz-5hUT5VhE'
    #RECAPURL = ''

    # XXX www.tvonline.tw is a sister site - looks like the same
    # markup/backend.

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + \
               '/search.php?q=' + \
               self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return 'no movies found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        if link:
            self.log.debug('-----------------')
            return self.BASE_URL + '/' + link['href']

    def search(self, search_term, media_type, **extra):
        search_url = self._fetch_search_url(search_term, media_type)
        soup = self.get_soup(search_url)
        if soup.select_one('div.g-recaptcha'):
            soup = self.post_soup(
                search_url,
                data={
                    'g-recaptcha-response': self.get_recaptcha_token(),
                    'submit': 'SUBMIT'
                }
            )

            self.save_session_cookies()
            self._parse_search_result_page(soup)




    def _parse_search_result_page(self, soup):
        results = soup.select('div.movie-list div.ml-data h1 a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result['href']
            if link.find('http:') == -1:
                link = 'http:' + link
            self.submit_search_result(
                link_url= link,
                link_title=result['title'],
                image=self.util.find_image_src_or_none(result, 'img')
            )

            next_button = self._fetch_next_button(soup)
            if next_button and self.can_fetch_next():
                soup = self.get_soup(next_button)
                self._parse_search_result_page(soup)


    @cacheable()
    def _extract_video(self, link_id):
        response = self.post(
            '{}/getlink.php?Action=get&lk={}'.format(self.BASE_URL, link_id)
        )
        link_url = response.text
        if link_url.startswith('//'):
            link_url = 'http:' + link_url
        return link_url


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for result in soup.select('div.links ul'):
            link = result.select_one('li.link-button a')
            if link:
                # Extract out the link id from
                # <a href="?lk=d2yF0Y2hlcnMudG8veWY1dGo0Zzc1NjM2LmhP0bWw="
                link_id = link['href'][4:]
                link_url = self._extract_video(link_id)
                if link_url:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_title=link.get('title', None),
                        link_url=link_url,
                    )


