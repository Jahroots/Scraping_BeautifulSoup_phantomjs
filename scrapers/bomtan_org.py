# coding=utf-8
import json
import urllib
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class BomtanOrg(SimpleScraperBase):
    BASE_URL = 'http://bomtan.org'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    REQUIRES_WEBDRIVER = True
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type=None, page=1):
        self.start = page
        self.search_term = search_term
        return '{base_url}/full-hd/{search_term}/page-{page}.html'.format(base_url=self.BASE_URL,
                                                                            search_term=search_term,
                                                                            page=page)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup.text).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, page=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _fetch_no_results_text(self):
        return u'Không tìm thấy kết'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.poster > a'):
            button_watch = self.get_soup(self.BASE_URL+result.href).select_one('a.btn-watch')['href']
            if 'javascript' in button_watch:
                continue
            links = self.get_soup(button_watch).select('a.chapter')
            for link in links:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        url_text = soup.find('div', id='player').find('script').text
        url_id = re.search('url = \"(.*)\";var', url_text)
        if url_id:
            url_id = url_id.groups()[0]
        name = re.search('name\s+= \"(.*)\";', url_text)
        if name:
            name = name.groups()[0]
        api_url = 'http://player6.bomtan.org/jwplayer7/?url={}&name={}&sub=&_=1494366456819'.format(url_id, name)
        iframe_url_text = self.get(api_url, headers={'referer':soup._url}).text
        if iframe_url_text:
            iframe_url = ''
            try:
                iframe_url = self.make_soup(iframe_url_text).select_one('iframe')['src'].replace('/file/d/', '/get_video_info?docid=').replace('/preview', '')
            except TypeError:
                self.webdriver().get(soup._url)
                soup = self.make_soup(self.webdriver().page_source)
                video_url = soup.select_one('video[class="jw-video jw-reset"]')
                if video_url:
                    video_url = video_url['src']
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=video_url,
                        link_title=video_url,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
                self.webdriver().close()
            if iframe_url:
                links = urllib.unquote(self.get(iframe_url).text).split('|')
                for link in links:
                    if link.startswith('http'):
                        url = link.split(',')[0]
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=url,
                            link_title=url,
                            series_season=series_season,
                            series_episode=series_episode,
                        )