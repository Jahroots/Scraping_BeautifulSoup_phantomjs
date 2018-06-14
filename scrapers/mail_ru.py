# coding=utf-8

from sandcrawler.scraper import ScraperBase, AntiCaptchaImageMixin, CachedCookieSessionsMixin
import re
import json

class MailRu(AntiCaptchaImageMixin, CachedCookieSessionsMixin, ScraperBase):
    # class MailRu(ScraperBase, VideoCaptureMixin):
    BASE_URL = 'https://my.mail.ru'  # Fudge: Do not change this value (here),
    # it's used by
    # the framework to know this is a base class
    LONG_SEARCH_RESULT_KEYWORD = '2016'
    SINGLE_RESULTS_PAGE = True
    PARSE_RESULTS_FROM_SEARCH = True


    ITEMS_PER_PAGE = 50  # Use the default from the site.

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            'https://mail.ru')

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            'https://mail.ru')


    def _fetch_search_url(self, search_term, media_type):
        return "http://go.mail.ru/search_video?tsg=l&q={}&utf8in=1&num=200&ajax=1&rch=l".format(
            self.util.quote(search_term))

    def search(self, search_term, media_type, **extra):
        self.load_session_cookies()
        search_url = 'https://go.mail.ru/search_video?q={}&rf=go.mail.ru&fm=1'.format(search_term)
        soup = self.get_soup(search_url)
        img = soup.select_one('img.antirobot__img')
        items = []
        if img:
            img_url = 'https://go.mail.ru' + img['src']
            captcha_result = self.solve_captcha(img_url)
            self.log.debug(captcha_result)
            sid = soup.select_one('input[name="sqid"]')['value']
            soup = self.post_soup('https://go.mail.ru/ar', data = {'dest': 'video', 'q' : search_term, 'sqid':sid,
                                                       'back': 'https://go.mail.ru/search_video?q={}&rf=go.mail.ru&fm=1'.format(search_term),
                                                       'errback' : 'https://go.mail.ru/search_video?q=2016&rf=go.mail.ru&fm=1&frm=captcha_error',
                                                        'SequreWord' : captcha_result})
            self.save_session_cookies()


        one = soup.find('script', text=re.compile('STP.results.items'))
        has_any = False
        if one:
            items = json.loads(one.text.replace(';', '').split('STP.results.items = ')[1])
            has_any = True
            for item in items:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=item['url'],
                                         link_title=item['description'])


        results = soup.select('a[class*="js-videolist__item videolist__item"]')

        for result in results:
            has_any = True
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=result.href,
                                     link_title=result.text)

        if not has_any:
            return self.submit_search_no_results()


    def parse(self, parse_url, **extra):
        try:
            metadata_url = self.get(parse_url).text.split('"metadataUrl":"')[1].split('"')[0]
        except:
            metadata_url = self.get(parse_url).text.split('"metaUrl": "')[1].split('"')[0]
        if 'http:' not in metadata_url:
            metadata_url = 'http:'+metadata_url
        json_ = self.get(metadata_url).json()
        title = json_['meta']['title']
        for media in json_['videos']:
            url = media['url']

            self.submit_parse_result(index_page_title=title,  # soup.title.text.strip(),
                                     link_url='http:' + url if url.startswith('//') else url,
                                     link_title=title)
