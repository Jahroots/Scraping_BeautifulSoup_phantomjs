# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CachedCookieSessionsMixin, AntiCaptchaMixin
from sandcrawler.scraper.caching import cacheable
import re

class FiliserPl(AntiCaptchaMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'https://fili.tv'
    OTHERS_URLS = ['https://filiser.co', 'https://fili.tv', 'http://filiser.tv']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'pol'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    RECAPKEY = '6Ld2kAkUAAAAAOSbyB5_L2UL7C8t5zy6V5y0XaYB'
    RECAPURL = 'https://fili.tv/captchaResponse'
    USERNAME = 'Tursed'
    EMAIL = 'elizabethdtoups@jourrapide.com'
    PASSWORD = 'le9VooBai4sh'


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/szukaj?q={}'.format(self.util.quote(search_term))

    def get(self, url, **kwargs):
        return super(FiliserPl, self).get(url, allowed_errors_codes=[404,403, 522], **kwargs)

    def _fetch_no_results_text(self):
        return u'Brak wyników'

    def _fetch_next_button(self, soup):
        next_link = ''
        try:
            next_link = soup.find('a', text=u'»')['href']
        except TypeError:
            pass
        return next_link if next_link else None

    def _parse_search_results(self, soup):
        found = 0
        for results in soup.select('ul#resultList2 div.title'):
            result = results.find_previous('a')['href']
            if '/serial/' in result:
                result_soup = self.get_soup(self.BASE_URL+result)
                for result in result_soup.select('a.episodeNum'):
                    title = soup.select_one('h2.title')
                    result_ref = self.BASE_URL + result['href']
                    self.submit_search_result(
                        link_url= result_ref,
                        link_title=title
                    )
            else:
                title = results.text.strip()
                self.submit_search_result(
                    link_url=self.BASE_URL + result,
                    link_title=title
                )

            found = 1
        if not found:
           return self.submit_search_no_results()

    @cacheable()
    def _extract_link(self, url):
        self.log.info(
            'Extracting link for FiliserPl - %s', url
        )
        self.load_session_cookies()
        source = self.get(url).text
        if "$.post('/captchaResponse'," in source:
            # we need to solve a recap.
            self.log.info(
                'Solving captcha for FiliserPl - %s', url
            )
            self.post_soup(
                'https://fili.tv/captchaResponse',
                data={
                    'response': self.get_recaptcha_token()
                }
            )
            source = self.get(url).text
            self.save_session_cookies()

        search = re.search("var url = '(.*?)';", source)
        if search:
            return search.group(1)
        return None

    def _parse_parse_page(self, soup):
        title = soup.select_one('h2.title').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(soup._url)

        iframes = soup.select('#player iframe')
        for iframe in iframes:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe['src'],
                link_text=title,
                series_season=season,
                series_episode=episode,
            )

        ep_links_ref = soup.select('div#links li.line')

        for ep_link_ref in ep_links_ref:
            ep_link_ref = ep_link_ref['data-ref']
            fetch_url = '{}/embed?salt={}'.format(self.BASE_URL, ep_link_ref)
            link = self._extract_link(fetch_url)

            if link:
                self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_text=title,
                        series_season=season,
                        series_episode=episode,
                )
