# coding=utf-8
import json, requests, time, shutil, base64
from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, AntiCaptchaImageMixin


class VumooAt(CloudFlareDDOSProtectionMixin, AntiCaptchaImageMixin, SimpleScraperBase):
    BASE_URL = 'http://vumoo.li'
    OTHER_URLS = ['http://vumoo.at',]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    stop = False
    SINGLE_RESULTS_PAGE = True
    REQUIRES_WEBDRIVER = True


    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return self.BASE_URL + '/videos/fsearch/?search={}&r=1'.format(search_term)

    def _fetch_no_results_text(self):
        return u'No movie matched your search'

    def search(self, search_term, media_type, **extra):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
        ses = requests.Session()
        soup = self.make_soup(ses.get(self._fetch_search_url(search_term, media_type), headers=headers).text)
        id_num = soup.select('input')[-1]
        if id_num:
            response = requests.get('http://vumoo.li/videos/vcaptcha', headers=headers, cookies=ses.cookies.get_dict())
            if '~IDAT' in response.text:
                action = '1'
            elif '!IDAT' in response.text:
                action = '3'
            else:
                action = '2'
            id_num_name = id_num['name']
            id_num_value = id_num['value']
            data = {'action': action, id_num_name: id_num_value}
            post_soup = self.make_soup(ses.post(self._fetch_search_url(search_term, media_type), data=data, headers=headers).text)
            self._parse_search_result_page(post_soup)


    def _parse_search_result_page(self, soup):
        results = soup.select('article.movie_item')
        if not results:
            return self.submit_search_no_results()
        else:
            for result in results:
                link = result.select_one('a')
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def parse(self, parse_url, **extra):
        soup = self.make_soup(requests.get(parse_url).text)
        title = soup.select_one('h3.movie_title span').text.strip()
        index_page_title = self.util.get_page_title(soup)
        data_url = soup.select_one("button[class='mainServer server-button active-server']")
        if data_url or soup.select_one('video[class="jw-video jw-reset"]'):
            if not data_url: data_url = soup.select_one('video[class="jw-video jw-reset"]')['src']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=self.BASE_URL + '/api/plink?id={}&res=360'.format(data_url['data-url']),
                link_text=title,
            )

        else:
            results = soup.select('div[data-click]')
            for result in results:
                    if len(result['data-click']) > 2:
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=result['data-click'].strip(),
                            link_text=title,
                        )



