# -*- coding: utf-8 -*-
import re
import json

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, ScraperParseException, CloudFlareDDOSProtectionMixin


class WatchItVideosTV(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://watchemvideos.com'

    OTHER_URLS = ['http://watchitvideos.info', 'http://watchitvideos.co',
        'http://watchitvideos.me',
        'http://www.watchitvideos.tv',
        'http://watchitvideos.org'
    ]


    SINGLE_RESULTS_PAGE = True


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'


    def search(self, search_term, media_type, **extra):
        items = json.loads(self.post(
            '{}/wp-admin/admin-ajax.php'.format(self.BASE_URL),
            data={
                'action': 'ajaxy_sf',
                'sf_value': search_term,
                'search': 'false',
            }
        ).text)

        if not items:
            return self.submit_search_no_results()
        found = False
        for result in items['post'][0]['all']:
            found = True
            soup = self.get_soup(result['post_link'])
            link = soup.select_one('span.hdmovie a')
            self.submit_search_result(
                link_url=link.href,
                link_title=result['post_title'],
            )
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        video = soup.select_one('video.vjs-tech')
        if video:
            self.submit_parse_result(
                link_url=video['src'],
                index_page_title=index_page_title,
            )
            return

        # gTmts = [{"vjsp":"1","vid":"360","itag":"18"},{"vjsp":"1","vid":"360","itag":"22"}];
        # Gets slotted into
        # "http://watchitvideos.org/?vjsp=" + gTmts[i].vjsp + "&vid=" + gTmts[i].vid + "&itag=" + gTmts[i].itag)
        srch = re.search('gTmts = (\[.*?\])', str(soup))
        if srch:
            for video_params in json.loads(srch.group(1)):
                link = '{}/?vjsp={}&vid={}&itag={}'.format(
                    self.BASE_URL,
                    video_params['vjsp'],
                    video_params['vid'],
                    video_params['itag'],

                )
                link_url = self.get_redirect_location(link)
                self.submit_parse_result(
                    link_url=link_url,
                    index_page_title=index_page_title,
                )

        # Others embedded:
        # <a data-vid="&lt;IFRAME SRC=&quot;http://thevideos.tv/embed-tx6jv34ghogw-620x470.html&quot; webkitAllowFullScreen=&quot;true&quot; mozallowfullscreen=&quot;true&quot; allowfullscreen=&quot;true&quot; frameborder=&quot;0&quot; marginwidth=&quot;0&quot; marginheight=&quot;0&quot; scrolling=&quot;no&quot; width=&quot;100%&quot; height=&quot;470&quot;&gt;&lt;/IFRAME&gt;" href="#">Server 1</a>
        for link in soup.select('span.ext-vid a'):
            try:
                vid = link['data-vid']
            except KeyError:
                continue
            vidsoup = self.make_soup(self.util.unquote(vid))
            self._parse_iframes(vidsoup, 'iframe', index_page_title=index_page_title)

