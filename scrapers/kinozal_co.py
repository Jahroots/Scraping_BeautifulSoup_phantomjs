# coding=utf-8
import json
import re
from bs4 import Comment
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class KinozalCo(SimpleScraperBase):
    BASE_URL = 'http://kinogou.club'
    OTHER_URLS = ['http://kinozal.co']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type=None, page=1):
        return u'{}/search/?q={}'.format(
            self.BASE_URL,
            self.util.unquote(search_term)
        )

    def _fetch_no_results_text(self):
        return u'<span class="numShown73">0-0</span>'

    def _parse_search_result_page(self, soup):
        for result in soup.select('a.mainlink'):
            link = result.href
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _fetch_next_button(self, soup):
        for button in soup.select('a.swchItem span'):
            if button.text == u'»':
                return 'http:' + button.parent.href
        return None

    def get_data(self, text):
        video_token = re.search("""video_token: '(.*?)'""", text).groups(0)[0]
        content_type = re.search("""content_type: '(.*?)'""", text).groups(0)[0]
        mw_key = re.search("mw_key = '(.*?)'""", text).groups(0)[0]
        mw_pid = str(re.search("""mw_pid: (.*?),""", text).groups(0)[0])
        p_domain_id = str(re.search("""p_domain_id: (.*?),""", text).groups(0)[0])
        ad_attr = '0'
        debug = re.search("""debug: (.*?)""", text)
        if debug:
            debug = str(debug.groups(0)[0])
            data = {'video_token': video_token, 'content_type': content_type, 'mw_key': mw_key, 'mw_pid': mw_pid,
                    'p_domain_id': p_domain_id, 'ad_attr': ad_attr,
                    'debug': debug}
            mw_value = re.search("""\] = \'(.*)\'""", text).groups()[0]
            key = re.search("""\w+\[\'(.*)\'\] =""", text).groups()[0]
            data[key] = mw_value
            return data

        return None


    def get_urls(self, url, soup_url):
            headers = {'Referer': soup_url}
            moonwalk_text = self.get(url, headers=headers).text
            data = self.get_data(moonwalk_text)
            headers = {'Referer': url,
                       'X-Requested-With': 'XMLHttpRequest', 'X-Iframe-Option': 'Direct'}
            if 'moonwalk' in url:
                m3u8_link = \
                    json.loads(self.post_soup('http://moonwalk.cc/sessions/new_session', data=data, headers=headers).text)[
                        'mans']['manifest_m3u8']
            else:
                m3u8_link = \
                    json.loads(
                        self.post_soup('http://serpens.nl/sessions/new_session', data=data, headers=headers).text)[
                        'mans']['manifest_m3u8']
            urls_list = self.get_soup(m3u8_link).text
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_.&+])+', urls_list)
            return urls


    def parse(self, parse_url, **extra):
        soup = self.make_soup(self.get(parse_url).text)

        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('span.name-ru')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(soup._url)

        text_urls = self.make_soup(str(soup.select_one('textarea[class="text hide"]')).replace('<!--', '').replace('-->',''))

        for url in text_urls.select('iframe') + text_urls.select('embed'):
            url = url['src']
            if 'http' not in url:
                url = 'http:' + url

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url= url,
                link_title= soup.select_one('h1.title').text,
                series_season=series_season,
                series_episode=series_episode,
            )

