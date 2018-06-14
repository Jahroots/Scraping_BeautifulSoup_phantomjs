# -*- coding: utf-8 -*-

from time import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin


class OnlineLife(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.online-life.club'
    OTHER_URLS = ['http://www.online-life.in', 'http://online-life.me', 'http://www.online-life.cc']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'rus'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 15
        self.media_type_to_category = 'film 0, tv 0'
        self.encode_search_term_to = 'cp1251'
        # self.showposts = 0

    def _parse_search_result_page(self, soup):
        for link in soup.select('.line a'):
            self.submit_search_result(
                link_title=link.text,
                link_url=link.href
            )

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов'

    def _fetch_next_button(self, soup):
        self.log.debug('------------------------')
        return soup.find('a', dict(name='nextlink'))

    def _parse_parse_page(self, soup):
        title = soup.select_one('.fullstory_title')
        series_season = series_episode = ''
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        # thanks to https://github.com/mrstealth/xbmc-gotham
        id_ = soup._url.split('/')[-1].split('-')[0]
        url = "http://dterod.com/js.php?id=%s" % id_
        # print "************ URL %s" % url

        link = list(self.util.find_urls_in_text(
            self.get(url, headers=dict(Referer=self.BASE_URL, Host='www.online-life.cc')).text))[0].replace(
            'www.online-life.cc', 'dterod.com')
        self.log.debug(link)

        is_movie = not link.endswith('.txt')
        is_season = link.endswith('.txt')

        if is_movie:
            # uri = self.BASE_URL + '/?mode=play&url=%s' % self.util.quote_plus(link)
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link,
                                     link_title=title,
                                     series_season=series_season,
                                     series_episode=series_episode,
                                     )

        elif is_season:
            self.log.debug("This is a season %s" % link)
            resp = self.get(link + '?rand={}'.format(time() / 10000000000))

            if resp.status_code == 200:
                resp = eval(resp.content.replace('\t', '').replace('\r\n', ''))

                if 'playlist' in resp['playlist'][0]:
                    self.log.debug("This is a season multiple seasons")

                    for season in resp['playlist']:
                        episods = None
                        try:
                            episods = season['playlist']
                        except KeyError:
                            pass
                        if episods:

                            for episode in episods:
                                # etitle = "%s (%s)" % (episode['comment'], common.stripTags(season['comment']))
                                url = episode['file']
                                # uri = self.BASE_URL + '/?mode=play&url=%s' % self.util.quote_plus(url)
                                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                         link_url=url,
                                                         link_title=title,
                                                         series_season=series_season,
                                                         series_episode=series_episode,
                                                         )

                else:
                    self.log.debug("This is one season")
                    for episode in resp['playlist']:
                        etitle = episode['comment']
                        url = episode['file']
                        # uri = self.BASE_URL + '/?mode=play&url=%s' % self.util.quote(url)

                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=url,
                                                 link_title=etitle,
                                                 series_season=series_season,
                                                 series_episode=series_episode,
                                                 )

        # old code
        try:
            for ifr in soup.find_all('iframe', width="730"):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=ifr['src'],
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )

            flashvar = soup.find('param', dict(name="flashvars"))
            if flashvar:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=flashvar.attrs['value'].split('download=')[1].split('&sub')[0],
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )
        except:
            pass
