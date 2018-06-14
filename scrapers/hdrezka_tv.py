# coding=utf-8

import json
import re
import urllib
import urllib2
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import selenium.common.exceptions

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class HDRezkaTv(SimpleScraperBase):
    BASE_URL = 'http://hdrezka.ag'
    OTHERS_URLS = ['http://hdrezka.me']
    NO_RESULTS_KEYWORD = '%^$'
    ALLOW_FETCH_EXCEPTIONS = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in (self.BASE_URL, 'http://hdrezka.tv'):
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.requires_webdriver = ('parse',)
        # self.adblock_enabled = False
        self.webdriver_type = 'phantomjs'  # cannot use

    def _fetch_no_results_text(self):
        return u'Для поиска необходимо ввести побольше символов'

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], verify=False, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        """
        Return a GET url for the search term; this is common, but you
         will often need to override this.
        """
        return self.BASE_URL + '/?do=search&subaction=search&q=' + \
               self.util.quote(search_term)  # .encode('utf8'))

    def _fetch_next_button(self, soup):
        link = soup.find('span',
                         attrs={'class': 'b-navigation__next i-sprt'})
        if link and link.parent and 'href' in link.parent.attrs:
            return link.parent['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.b-content__inline_item'):
            title = result.select(
                'div.b-content__inline_item-link a')[0].text
            img = result.select('a > img')[0]
            if img:

                self.submit_search_result(
                    link_url=result['data-url'],
                    link_title=title,
                    image=img['src'],
                )
            else:
                self.submit_search_result(
                    link_url=result['data-url'],
                    link_title=title,

                )
    def get_data(self, text):
        video_token = re.search("""video_token: '(.*?)'""", text).groups(0)[0]
        content_type = re.search("""content_type: '(.*?)'""", text)
        if content_type:
            content_type = content_type.groups(0)[0]
            mw_key = re.search("mw_key = '(.*?)'""", text).groups(0)[0]
            mw_pid = str(re.search("""mw_pid: (.*?),""", text).groups(0)[0])
            p_domain_id = str(re.search("""p_domain_id: (.*?),""", text).groups(0)[0])
            ad_attr = '0'
            data = {'video_token': video_token, 'content_type': content_type, 'mw_key': mw_key, 'mw_pid': mw_pid,
                    'p_domain_id': p_domain_id, 'ad_attr': ad_attr,
                    }
            return data

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(soup._url)
        episodes=soup.select_one('div#simple-episodes-tabs')
        if episodes:
            iframe_link = soup.select_one('#cdn-player')['src']
            for ids in episodes.find_all('li'):
                season = ids['data-season_id']
                episode = ids['data-episode_id']
                season_episode = 'season={}&episode={}'.format(season, episode)
                iframe_link = iframe_link.split('?')[0]+'?nocontrols=1&'+season_episode
                headers = {'Referer': soup._url}

                return self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe_link,
                    link_title=title.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

                cdn_soup = self.get_soup(iframe_link, headers=headers)
                cdn_domain = iframe_link[:26]
                cdn_text = cdn_soup.text
                data = self.get_data(cdn_text)
                mw_value = re.search("""\] = \'(.*)\'""", cdn_soup.text)
                if mw_value:
                    mw_value = mw_value.groups()[0]
                    key = re.search("""\w+\[\'(.*)\'\] =""", cdn_soup.text).groups()[0]
                    data[key] = mw_value
                    x_access = re.search("""X-Access-Level\': \'(.*?)\'""", cdn_soup.text).groups()[0]

                    headers = {'X-Access-Level': x_access, 'X-Requested-With': 'XMLHttpRequest'}
                    m3u8_link = json.loads(
                                self.post_soup('{}/sessions/new_session'.format(cdn_domain), data=data, headers=headers).text)[
                                'mans']['manifest_m3u8']
                    urls_list = self.get_soup(m3u8_link).text
                    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_.&+])+', urls_list)
                    for url in urls:
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=url,
                            link_title=url,
                            series_season=season,
                            series_episode=episode,
                        )

        else:
            iframe_link = soup.select_one('#cdn-player')

            headers = {'Referer': soup._url}
            cdn_soup = ''
            try:
                cdn_soup = self.get_soup(iframe_link['src'], headers=headers)
            except Exception as e:
                self.log.warning(str(e))
                return

            cdn_domain = iframe_link['src'][:26]

            cdn_text = cdn_soup.text
            data = self.get_data(cdn_text)
            mw_value = re.search("""\] = \'(.*)\'""", cdn_soup.text)
            if mw_value:
                mw_value = mw_value.groups()[0]
                key = re.search("""\w+\[\'(.*)\'\] =""", cdn_soup.text).groups()[0]
                data[key] = mw_value
                x_access = re.search("""X-Access-Level\': \'(.*?)\'""", cdn_soup.text).groups()[0]
                headers = {'X-Access-Level': x_access, 'X-Requested-With': 'XMLHttpRequest'}

                if 'video' in cdn_soup._url:
                    return self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=cdn_soup._url,
                        link_title=title.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )


                m3u8_link = json.loads(
                            self.post_soup(self.BASE_URL + '/manifests/video/{}/all'.format(cdn_domain), data=data, headers=headers).text)[
                            'mans']['manifest_m3u8']
                urls_list = self.get_soup(m3u8_link).text
                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_.&+])+', urls_list)
                for url in urls:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=url,
                        link_title=url,
                        series_season=series_season,
                        series_episode=series_episode,
                    )

