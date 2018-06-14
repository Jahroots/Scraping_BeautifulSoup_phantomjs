# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, \
    AntiCaptchaImageMixin, ScraperParseException
import re

class YeuhdNet(SimpleScraperBase, AntiCaptchaImageMixin):
    BASE_URL = 'http://yeuhd.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]


    VERIFY_CACHE_KEY = 'yeuhdnet_captcha'

    def get(self, url, **kwargs):
        # Site does a region check,
        self._http_session.cookies.set(
            'PLTV__geoip_confirm',
            '1',
            domain='yeuhd.net')
        return super(YeuhdNet, self).get(url, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return u'{}/tim-kiem/{}/'.format(
            self.BASE_URL,
            self.util.quote(search_term)
        )

    def _fetch_no_results_text(self):
        return u'Không tìm thấy kết quả nào phù hợp với truy vấn của bạn.'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a[class="page-link active"]')
        if next_button:
            return next_button.next_sibling.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div[class*="movie-item"] div.hvr-inner a'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _extract_streams(self, url):
        links = []
        if not url:
            return []
        source = self.get(url).content
        # Extract some vars out of javascript.
        srch1 = re.search("filmInfo\.filmID = parseInt\('(\d+)'\);",
                          source)
        if srch1:
            for link in self.make_soup(source).select('div.list-server div.server a'):
                hash = link['data-hash']
                if not hash:
                    continue
                video_info = self.post(
                    u'{}/ajax/player'.format(self.BASE_URL),
                    data={
                        'link': hash,
                        'id': srch1.group(1),
                    }
                ).json()
                if 'link' in video_info:
                    # An error messgae.
                    if isinstance(video_info['link'], basestring):
                        continue
                    for file_info in video_info['link'].values():
                        links.append(file_info['file'])

        return links

    def _find_captcha(self):
        self._http_session.cookies.pop(
            'PHPSESSID',
        )
        verify = self.solve_captcha(
            '{}/ajax/captcha/rand/'.format(self.BASE_URL)
        )
        result = (self._http_session.cookies.get('PHPSESSID'), verify)
        from sandcrawler.scraper.caching import cache
        cache.store_pickle(
            self.VERIFY_CACHE_KEY,
            result
        )
        return result


    def _extract_downloads(self, url):
        links = []
        if not url:
            return []

        # Pull the id out of the url.
        srch = re.search('(\d+)/download.html', url)
        if not srch:
            return []
        video_id = srch.group(1)

        # This site has a session based captcha, which appears to be reusable.
        # Grab our php sess id and veify out of the cache and try to submit
        from sandcrawler.scraper.caching import cache
        import redis_cache

        try:
            phpsessid, verify = cache.get_pickle(
                self.VERIFY_CACHE_KEY
            )
        except (redis_cache.ExpiredKeyException,
                redis_cache.CacheMissException,
                TypeError
                ):
            self.log.debug('Failed loading session and verify from cache.')
            phpsessid, verify = self._find_captcha()

        self._http_session.cookies.set(
            'PHPSESSID',
            phpsessid,
            domain='yeuhd.net'
        )

        response = self.post(
            u'{}/ajax/download'.format(self.BASE_URL),
            data={
                'download[verify]': verify,
                'download[filmId]': video_id,
            }
        ).json()
        if not response['_fxStatus']:
            # Solve the captcha.
            phpsessid, verify = self._find_captcha()
            self._http_session.cookies.set(
                'PHPSESSID',
                phpsessid,
                domain='yeuhd.net'
            )
            response = self.post(
                u'{}/ajax/download'.format(self.BASE_URL),
                data={
                    'download[verify]': verify,
                    'download[filmId]': video_id,
                }
            ).json()
            if not response['_fxStatus']:
                raise ScraperParseException('Failed to find captcha')


        soup = self.make_soup(response['_fxHtml'])
        for link in soup.select('a'):
            # Pull out (and later cache?) the id from this url.
            srch = re.search(
                'download-(\d+)\.html',
                link.href,
            )
            if srch:
                downloadid = srch.group(1)
                download_soup = self.post_soup(
                    u'{}/ajax/download'.format(self.BASE_URL),
                    data={
                        'loadUrlDown': 1,
                        'episodeId': downloadid,
                    }
                )
                for link in download_soup.select('a'):
                    links.append(link.href)

        return links

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)


        # Two sets of links - download and stream.
        for link in soup.select('div[class="btn-transform transform-vertical red"] a'):
            #self._extract_downloads(soup.select_one('a#btn-film-download').href) + \

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                series_season=series_season,
                series_episode=series_episode,
            )
