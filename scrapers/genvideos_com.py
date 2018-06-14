# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase

import time

class Resp(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class GenVideos(SimpleScraperBase):
    BASE_URL = 'https://genvideos.com'
    OTHER_URLS = ['http://genvideos.com']

    COOKIE_NAMES = (
        '__cfduid',
        'cf_clearance',
        'rc',
        'PHPSESSID',
        'begin_referer',
        'ci_session',

    )

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


    def get(self, url, **kwargs):
        return super(GenVideos, self).get(url, allowed_errors_codes=[403, 404, 503], **kwargs)


    def search(self, *args, **kwargs):
        self.get(self.BASE_URL)
        self.page = 1
        return super(GenVideos, self).search(*args, **kwargs)


    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        self.TERM = search_term
        return u'{}/results?q={}'.format(
            self.BASE_URL, self.util.quote(search_term)
        )

    def _fetch_next_button(self, soup):
        self.page += 1
        paging = soup.select_one('div.paging')
        if paging:
            page = paging.find('a', text=str(self.page))
            if page:
                return u'{}{}'.format(self.BASE_URL, page.href)
        return None

    def fetch_last_page(self, soup):
        if soup.find('a', text='>>'):
            return self.BASE_URL + soup.find('a', text='>>')['href']
        else:
            return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.video_title h3 a')

        found = False
        for result in results:
            self.log.warning(result)
            found = True
            self.submit_search_result(
                link_url=u'{}{}'.format(self.BASE_URL, result['href']),
                link_title=result.text
            )
        if not found and self.page == 1:
            self.submit_search_no_results()

        time.sleep(30)

    def parse(self, parse_url, **extra):
        video_id_search = re.search(
            'watch_(.*)\.html',
            parse_url,
        )
        if video_id_search:

            # THis sets a 'watch' cookie.
            soup = self.get_soup(parse_url)
            index_page_title = self.util.get_page_title(soup)

            frame_url = 'http:' +  re.search('frame_url.*;', soup.text).group(0).split('=')[1].replace('"', '').replace(';', '').strip()
            self.log.warning(frame_url)


            self.submit_parse_result(
                            link_url=frame_url,
                            index_page_title=index_page_title
            )
