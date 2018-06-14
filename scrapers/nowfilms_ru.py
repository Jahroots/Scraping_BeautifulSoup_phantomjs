# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin, UppodDecoderMixin
import re


class Nowfilms(OpenSearchMixin, UppodDecoderMixin, SimpleScraperBase):
    BASE_URL = 'http://kinokongo.cc'
    OTHER_URLS = ['http://kinokong.cc', 'http://kinokongo.cc']
    LONG_SEARCH_RESULT_KEYWORD = '2017'
    TRELLO_ID = 'udY9RlC0'

    def setup(self):
        raise NotImplementedError('Duplicate KinogoCo')
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
        #self.bunch_size = 200
        # self.media_type_to_category = 'tv 35, film 1'
        #self.encode_search_term_to = 'cp1251'
        #self.showposts = 1

    def _fetch_search_url(self, search_term):

        return self.BASE_URL + '/'

    def _parse_search_result_page(self, soup):
        #self.log.debug(soup)
        for link in soup.select('a.main-sliders-play'):
            if not 'recenziya-k-filmu' in link.href:
                self.submit_search_result(
                    link_title=link.text,
                    link_url=link.href
                )

    def _parse_parse_page(self, soup):
        if u'Трейлеры' in soup.select_one('.fullstory-drops').text:
            return

        title = soup.select_one('.full-kino-title h1').text
        series_season, series_episode = self.util.extract_season_episode(title)
        script_text = soup.find('script', text=re.compile(',pl:'))
        if script_text:
            url = re.search(',pl:.+,', script_text.text)
            for link in self.util.find_urls_in_text(url.group(0)):

                self.log.debug(self.decode(link))


        return

        try:
            url = str(soup).split(',"file":"')[1].split('"};')[0]
            if ',' in url:
                urls = url.split(',')
            else:
                urls = [url]
            for url in urls:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url,
                                         link_title=title,
                                         series_season=series_season,
                                         series_episode=series_episode,
                                         )
        except Exception as e:
            self.log.warning(e)

        try:
            flashvars = soup.find('param', {'name': 'flashvars'})['value']

            if '&pl=' in flashvars:
                url2dl = flashvars.split('&pl=')[0].split('"')[1]
                for epis in self.get(url2dl).json()['playlist']:
                    if ',' in epis['file']:
                        for url in epis['file'].split(','):
                            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                     link_url=url,
                                                     link_title=title,
                                                     series_season=series_season,
                                                     series_episode=series_episode,
                                                     )
                    else:
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=epis['file'],
                                                 link_title=title,
                                                 series_season=series_season,
                                                 series_episode=series_episode,
                                                 )

            try:
                media_file = flashvars.split('file:"')[1].split('"')[0]
                if ' or ' in media_file:
                    media_file = media_file.split(' or ')
                elif ',' in media_file:
                    media_file = media_file.split(',')

                media_file = [media_file] if isinstance(media_file, basestring) else media_file
                for url in media_file:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=url,
                                             link_title=title,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )
            except Exception as e:
                self.log.debug(e.__class__.__name__)

            try:
                media_file = flashvars.split('"file":"')[1].split('"}')[0]
                if ' or ' in media_file:
                    media_file = media_file.split(' or ')
                elif ',' in media_file:
                    media_file = media_file.split(',')

                media_file = [media_file] if isinstance(media_file, basestring) else media_file
                for url in media_file:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=url,
                                             link_title=title,
                                             series_season=series_season,
                                             series_episode=series_episode,
                                             )

            except Exception as e:
                self.log.debug(e.__class__.__name__)

        except Exception as e:
            # self.log.exception(e)

            if ',pl:"' in str(soup):
                url2dl = str(soup).split(',pl:"')[1].split('"')[0]

                try:
                    jsonny = self.get(url2dl).json()
                except ValueError:
                    import json
                    jsonny = json.loads(self.get(url2dl).text.replace(u'\u043f\xbb\u0457', ''))

                for epis in jsonny['playlist']:
                    if ',' in epis['file']:
                        for url in epis['file'].split(','):
                            if url:
                                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                         link_url=str(url),
                                                         link_title=title,
                                                         series_season=series_season,
                                                         series_episode=series_episode,
                                                         )
                    else:
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=epis['file'],
                                                 link_title=title,
                                                 series_season=series_season,
                                                 series_episode=series_episode,
                                                 )
