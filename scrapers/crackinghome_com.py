# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class CrackingHomeCom(SimpleScraperBase):
    BASE_URL = 'http://crackinghome.com'

    LONG_SEARCH_RESULT_KEYWORD = 'dvdscr'

    def setup(self):

        raise NotImplementedError('Paid subscription for infringing content.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _login(self):
        soup = self.get_soup(self.BASE_URL)
        csrf_key = soup.find('input', dict(name="csrfKey")).attrs['value']
        self.post(self.BASE_URL + '/login/',
                  data=dict(login__standard_submitted='1',
                            csrfKey=csrf_key,
                            auth='znjsvioh@zetmail.com',
                            password='888Sands',
                            remember_me='0',
                            remember_me_checkbox='1',
                            signin_anonymous='0'
                            ))

        # 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' - H
        # 'Accept-Encoding: gzip, deflate' - H
        # 'Accept-Language: en-GB,en;q=0.5' - H
        # 'Connection: keep-alive' - H
        # 'Cookie: __cfduid=d85068b8f8edbd06fb15b701bd46a6d491464181460; ips4_member_id=1691; ips4_IPSSessionFront=pipb34h7mu6k1b1l3fekjbvsb2; ips4_ipsTimezone=Asia/Dhaka; ips4_hasJS=true' - H
        # 'Host: crackinghome.com' - H
        # 'Referer: http://crackinghome.com/topic/9372-batman-v-superman-dawn-of-justice-2016-hc-dvdscr-950mb-mkvcage/?do=findComment&comment=20297' - H
        # 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:46.0) Gecko/20100101 Firefox/46.0' - H
        # 'Content-Type: application/x-www-form-urlencoded' - -data

    def search(self, search_term, media_type, **extra):
        self._login()
        soup = self.get_soup(self._fetch_search_url(search_term, media_type), allowed_errors_codes=[429])
        self._parse_search_results(soup)

    def get(self, url, **kwargs):
        kwargs['allowed_errors_codes'] = [429]
        return super(self.__class__, self).get(url, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?type=forums_topic&q=' + \
               search_term

    def _fetch_no_results_text(self):
        return 'Found 0 results'

    def _fetch_next_button(self, soup):
        link = soup.select_one('li.ipsPagination_next a')
        self.log.debug('------------------')
        return link['href'] if link else None

    def parse(self, parse_url, **extra):
        self._login()
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_search_result_page(self, soup):
        for result in soup.select('li.ipsStreamItem h2.ipsStreamItem_title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        body = soup.select_one('div.cPost_contentWrap')
        image = self.util.find_image_src_or_none(body, 'img')
        for link in self.util.find_urls_in_text(unicode(body), skip_images=True):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link,
                                     image=image,
                                     )
