# coding=utf-8

import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, AntiCaptchaMixin, CachedCookieSessionsMixin
from sandcrawler.scraper.caching import cacheable


class BsTo(AntiCaptchaMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'https://bs.to'
    RECAPKEY = "6LeiZSYUAAAAAI3JZXrRnrsBzAdrZ40PmD57v_fs"

    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'girls'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "deu"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, **kwargs)

    def post(self, url, **kwargs):
        return super(self.__class__, self).post(url, verify=False, headers={'Referer': u'{}/search'.format(self.BASE_URL)}, **kwargs)

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(
            self.BASE_URL + '/search',
            data={
                "search[text]": search_term,
                "search[series]": 0,
                "search[season]": '',
            }
        )
        self._parse_search_results(soup)

    def _fetch_no_results_text(self):
        return 'Es wurden keine Ergebnisse gefunden!'

    def _fetch_next_button(self, soup):
        return None

    def _find_season_episode(self, text):
        srch = re.search('Staffel (\d+), Episode (\d+)', text, )
        if srch:
            return srch.groups()
        return None, None

    def _parse_search_result_page(self, soup):
        for result in soup.select('section.suche ul li'):
            link = result.find('a')
            if not link:
                continue
            series_season, series_episode = self._find_season_episode(
                result.text)
            self.submit_search_result(
                link_url=self.BASE_URL + '/' + link['href'],
                link_title=result.text.strip(),
                series_season=series_season,
                series_episode=series_episode
            )

    @cacheable()
    def get_captcha_link(self, iframe_link):
            out_soup = self.get_soup(iframe_link)
            if 'grecaptcha' in out_soup.text:
                key = self.get_recaptcha_token()
                iframe_link = self.get_redirect_location(iframe_link + '?token=' + key)
            return iframe_link

    def _parse_parse_page(self, soup):
        title = soup.select_one('div h2')
        if title and title.text:
            title = title.text
        links = soup.select('ul[class="hoster-tabs top"] li a')
        for link in links:
            soup = self.get_soup(self.BASE_URL + '/' + link.href)
            iframe = soup.select_one('iframe')
            if iframe and iframe['src']:
                if '/out/' in iframe['src']:
                    movie_url = self.get_captcha_link(iframe['src'])
                    self.submit_parse_result(
                        index_page_title=self.util.get_page_title(soup),
                        link_url=movie_url,
                        link_text=title
                    )


