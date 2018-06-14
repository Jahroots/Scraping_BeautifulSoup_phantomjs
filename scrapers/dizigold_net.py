# coding=utf-8


import base64, json
import itertools
from sandcrawler.scraper.caching import cacheable
from sandcrawler.scraper import ScraperBase, AntiCaptchaMixin, CachedCookieSessionsMixin, ScraperParseException


class DizigoldNet(AntiCaptchaMixin, CachedCookieSessionsMixin, ScraperBase):
    BASE_URL = 'http://www.dizigold5.com'
    OTHER_URLS = ['http://www.dizigold4.com', 'http://www.dizigold2.com','http://www.dizigold1.com', 'http://player.dizigold.org', 'http://www.dizigold.net', 'http://m.dizigold.org', ]
    # Note - this has changed a few times; if we're not gettnig results, that may
    # be the cause.
    PLAYER_URL = 'http://player.dizigold1.com'
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]

    RECAPKEY = '6Le-cQgTAAAAAJVrvlU9ddmbEPuYskQaPjEBlsXe'
    RECAPURL = 'http://www.dizigold1.com'

    def post(self, url, **kwargs):
        kwargs['headers']={'X-Requested-With':'XMLHttpRequest'}
        return super(self.__class__, self).post(url, verify=False, **kwargs)

    @cacheable()
    def _extract_link(self, iframe_link):
        self.load_session_cookies()
        soup = self.get_soup(iframe_link)
        if soup.select('div.g-recaptcha'):
            soup = self.post_soup(
                'http://player.dizigold1.com/control',
                data={
                    'g-recaptcha-response': self.get_recaptcha_token()
                }
            )
            if 'Captcha incorrecto' in unicode(soup):
                raise ScraperParseException('Invalid captcha returned')
            self.save_session_cookies()
        link = soup.select_one('iframe')
        if link:
            link = link['src']
            return link
        else:
            player_script_text = soup.select_one('div#player').find_next('script').text
            return filter(None, list(self.util.find_file_in_js(player_script_text)))


    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/sistem/ajax.php',
                data={
                    'aranan':self.util.quote(search_term),'tip':'aranans',
                }
            )
        )

    def _parse_search_results(self, soup):
        self.block = False
        for result in soup.select('a'):
            title = result.find('h3').text.split('IMDB')[0].strip()
            link = result['href'].strip('\\"').replace("\\", '')
            series_soup = self.get_soup(link)
            for series_links in series_soup.select('div.playlist-content a.realcuf')+series_soup.select('a.season'):
                self.submit_search_result(
                    link_url=series_links['href'],
                    link_title=title,
                )
                self.block = True
        if not self.block:
            return self.submit_search_no_results()

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403,], **kwargs)

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        title = soup.select_one('h1').text.strip()
        season, episode = self.util.extract_season_episode(title)
        id_iframe = soup.text.split('view_id="')[-1].split('"')[0]
        season_id = soup.text.split('sezon_id="')[-1].split('"')[0]
        data = {'dil': 'tr', 'id': id_iframe, 'tip': 'view', 's': 1, 'sezon_id': season_id}
        post_page = json.loads(self.post(self.BASE_URL + '/sistem/ajax.php', data=data).text)
        nums_s = post_page['alternatives']
        for num_s in nums_s:
            data = {'dil': num_s['lang'],'s':str(num_s['trigger']),'id':id_iframe, 'tip':'view', 'sezon_id':season_id}
            post_season = json.loads(self.post(self.BASE_URL + '/sistem/ajax.php', data=data).text)
            m_link = self.make_soup(post_season['data']).select_one('iframe')
            if m_link:
                alt_link = m_link['src']
                links_soup = self.get_soup(alt_link)
                script_links = self.util.find_file_in_js(links_soup.text)
                for link in script_links:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                              link_url=link,
                                              link_title=title,
                                              series_season=season,
                                              series_episode=episode,
                                              )
                iframe_link = links_soup.select_one('iframe')
                if iframe_link:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=iframe_link['src'],
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode,
                                             )
