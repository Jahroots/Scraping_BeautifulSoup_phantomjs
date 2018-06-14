# coding=utf-8

import re
import base64
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperFetchException
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable



class LibertyLandTv(SimpleScraperBase):
    BASE_URL = 'https://libertyvf.net'
    OTHER_URLS = ['http://libertyvf.net','http://libertyvf.com', 'http://libertyland.co']
    COOKIE_NAMES = CloudFlareDDOSProtectionMixin.COOKIE_NAMES + \
                   ('g-recaptcha-response',
                    'ecdsa_sign',
                    'PHPSESSID',
                    )
    LONG_SEARCH_RESULT_KEYWORD = 'the'
    USER_AGENT_MOBILE = False
    TRELLO_ID = 'FLzy9BAX'

    def get(self, url, **kwargs):
        return super(LibertyLandTv, self).get(url, allowed_errors_codes=[403, 522], **kwargs)

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = "fra"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ]+ self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'
        self._request_connect_timeout = 400
        self._request_response_timeout = 400

    @cacheable()
    def _extract_protected_link(self, url):
        self.log.debug("Fetching recaptcha protected url: %s", url)
        wd = self.webdriver()
        # Get the base url - we can't set cookies until we have a real site...
        if wd.current_url.startswith('data'):  # First page on opening.
            wd.get(self.BASE_URL)
        else:
            need_to_get_base = False
            while not wd.current_url.startswith(self.BASE_URL):
                wd.back()
                if wd.current_url.startswith('data'):
                    need_to_get_base = True
                    break
            if need_to_get_base:
                wd.get(self.BASE_URL)
        for name, value, domain in self._get_cookies():
            wd.add_cookie({
                'name': name,
                'value': value,
                'domain': domain,
            })
        wd.get(url)
        # Sometimes it will just redirect if we already know the captcha result!
        if wd.current_url.startswith(self.BASE_URL):
            self.solve_recaptcha()
        return wd.current_url

    def _parse_parse_page(self, soup):
        # Find all links under the td.separateur_links and follow them.
        # if it remains local, probably an embedded stream so dig out an
        #  iframe.
        # Otherwise, submit that url.
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('a.ddl_link'):
            href = link['href']
            if not link['href'].startswith('http'):
                href = self.BASE_URL + href
            try:
                response = self.get(href)
            except ScraperFetchException:
                self.log.warning('Failed to fetch %s', href)
                continue
            if response.url.startswith(self.BASE_URL):
                # Sometimes we get a recaptcha!
                if 'https://www.google.com/recaptcha/' in response.content:
                    link_url = self._extract_protected_link(response.url)
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link_url,
                    )
                else:
                    link_soup = self.make_soup(response.content)
                    for iframe in link_soup.select('iframe'):
                        link_url = iframe['src']
                        if link_url.startswith('//'):
                            link_url = 'http:' + link_url
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=link_url,
                        )
            else:
                self.log.warning(response.url)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=response.url,
                    link_title=link.text,
                )

    def search(self, search_term, media_type, **extra):
        if media_type == ScraperBase.MEDIA_TYPE_TV:
            self._parse_tv_search_result_page(
                self.post_soup(
                    self.BASE_URL + '/v2/recherche/',
                    data={
                        'categorie': 'series',
                        'mot_search': search_term
                    }
                )
            )
        else:
            self._parse_movie_search_result_page(
                self.post_soup(
                    self.BASE_URL + '/v2/recherche/',
                    data={
                        'categorie': 'films',
                        'mot_search': search_term
                    }
                )
            )

    def _find_season_episode(self, text):
        match = re.search('Saison (\d+)\s*, Episode (\d+)', text)
        if match:
            return match.groups()
        return None, None

    def _parse_tv_search_result_page(self, soup):

        if str(soup).find(': 0 resultat(s)') >= 0 :
            return self.submit_search_no_results()

        for link, season_soup in self.get_soup_for_links(soup,
                                                         'div#fiche h2.heading a'):

            image = self.util.find_image_src_or_none(season_soup,
                                                     'div.avatar img')

            for ep_link in season_soup.select('a.num_episode'):
                season, episode = self._find_season_episode(
                    ep_link['title'])
                url = ep_link['href']
                if 'http' not in url:
                    url = self.BASE_URL + url
                self.submit_search_result(
                    link_url=url,
                    link_title=link.text + " " + ep_link['title'],
                    series_season=season,
                    series_episode=episode,
                    asset_type=ScraperBase.MEDIA_TYPE_TV,
                    image=image
                )

        next_link = soup.find('a', text=u'Suivant »')
        if 'http' not in next_link['href']:
            next_link = self.BASE_URL + next_link
        else:
            next_link = next_link['href']
        if next_link and self.can_fetch_next():
            self._parse_tv_search_result_page(
                self.get_soup(next_link)
            )

    def _parse_movie_search_result_page(self, soup):
        if str(soup).find(': 0 resultat(s)') >= 0:
            return self.submit_search_no_results()

        results = soup.select('div.bloc-generale')

        for index in range(2, len(results)):
            result = results[index]
            link = result.select_one('h2.heading a')
            image = self.util.find_image_src_or_none(result,
                                                     'img.img-responsive')
            if link:
                if link['href'].startswith('//'):
                    link['href'] = 'http:' + link['href']
                self.submit_search_result(
                    link_url=link['href'],
                    link_title=link.text,
                    image=image,
                    asset_type=ScraperBase.MEDIA_TYPE_FILM
                )

        next_link = soup.find('a', text=u'Suivant »')
        if 'http' not in next_link['href']:
            next_link = self.BASE_URL + next_link['href']
        else:
            next_link = next_link['href']
        if next_link and self.can_fetch_next():
            self._parse_movie_search_result_page(
                self.get_soup(next_link)
            )

    def get(self, url, **kwargs):
        return super(LibertyLandTv, self).get(url, allowed_errors_codes=[404, 403,], **kwargs)
