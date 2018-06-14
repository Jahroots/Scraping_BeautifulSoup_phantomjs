# coding=utf-8

import base64
import re
import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class SweFilmTv(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://swefilm.tv'

    OTHER_URLS = []

    LONG_SEARCH_RESULT_KEYWORD = 'san andreas'
    SINGLE_RESULTS_PAGE = True
    def setup(self):
        raise NotImplementedError('the website is deprecated')

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "dan"  # swe

        self.register_media(self.MEDIA_TYPE_FILM)
        self.register_media(self.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'


    def get(self, url, **kwargs):
        if 'allowed_errors_codes' in kwargs:
            kwargs['allowed_errors_codes'].append(404)
        else:
            kwargs['allowed_errors_codes'] = [404, ]
        return super(SweFilmTv, self).get(
            url, **kwargs)

    def _fetch_no_results_text(self):
        return 'Inga uppgifter!'

    def _fetch_search_url(self, search_term, media_type):
        return u'%s/search/%s' % (
            self.BASE_URL, self.util.quote(search_term.encode('utf-8')))

    def _fetch_next_button(self, soup):
        link = soup.find('a', {'title': 'Next'})
        if link:
            return self.BASE_URL + '/' + link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.m_list ul li > a'):
            # target is blank = ad.
            target = result.get('target', None)
            if target and target == '_blank':
                continue
            image = self.util.find_image_src_or_none(result, 'img')
            if image and not image.startswith('http'):
                image = self.BASE_URL + '/' + image
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.get('title', result.text).strip(),
                image=image,
            )

    def _submit_parses_from_soup(self, soup, ttl):
        # window.top.location = "http://tinyurl.com/jzyfzgk"

        for link in re.findall(
            'window.top.location = "(.*?)"',
            str(soup),
            ):
            self.submit_parse_result(
                index_page_title=ttl,
                link_url=link
            )



        # script>var cur1080p="";var cur720p="https://redirector.googlevideo.com/videoplayback?requiressl=yes&id=dd1128ecf5d1a6d7&itag=22&source=picasa&cmo=secure_transport=yes&ip=0.0.0.0&ipbits=0&expire=1437879290&sparams=requiressl,id,itag,source,ip,ipbits,expire&signature=B679F7B3FC737F492D74BC034CBA3EA2D1D0108F.C9C5E69B1316E9579C0EBD90ACD47311523CDC96&key=lh1";var cur480p="";var cur360p="https://redirector.googlevideo.com/videoplayback?requiressl=yes&id=dd1128ecf5d1a6d7&itag=18&source=picasa&cmo=secure_transport=yes&ip=0.0.0.0&ipbits=0&expire=1437879290&sparams=requiressl,id,itag,source,ip,ipbits,expire&signature=77A4F12DFD4BF38BDA6024E76327323D5889D9F1.1769A2EC8CCC3C6D939971BABCB503D4A5DBBC51&key=lh1";var curname="Supergirl Season 1";var cursub="/subtitle/4702.srt"</script>
        for link in re.findall(
                'var cur\d*p=\"([^"]*)"',
                str(soup)):
            if link:
                self.submit_parse_result(
                    index_page_title=ttl,
                    link_url=link
                )
        for video in soup.select('video'):

            for url in [line.split('src="')[1].split('">')[0] for line in str(video).split(' ') if
                        line.startswith('src=')]:
                # src = video.get('src', video.get('video-src', None))
                # if src:
                self.submit_parse_result(index_page_title=ttl,
                                         link_url=url
                                         )

        def do_ntimes(fn, arg, count):
            res = arg
            for i in range(count):
                res = fn(res)
            return res

        def extract_source_tags(html):
            source_tags = re.findall(r'(<source.*?\/>)', html)
            if source_tags:
                streams = []
                for source_tag in source_tags:
                    match = re.search(r'src=\'(.*?)\'.*?(label|data-res|res)="(.*?)"', source_tag)
                    if match:
                        streams.append((match.group(3), match.group(1)))

                return streams

        # html = str(soup)
        # print html
        # atob = re.search(r"atob\(\('(.*?)'\)", html)
        # atob_count = html.count('atob(')
        # if atob:
        #     base64_string = atob.group(1)
        #     content = do_ntimes(base64.b64decode, base64_string, atob_count)  # base64.b64decode(base64_string)
        #     video_sources = extract_source_tags(content)
        #     subtitles = 0 #extract_subtitles(content)
        #     return video_sources, subtitles

        htm = str(soup)
        if "window.atob(" in htm:
            atob_count = htm.count('atob(')
            code = htm.split("window.atob(('")[1].split("'")[0]
            repl = htm.split(".replace('")[1].split("'")[0]
            content = do_ntimes(base64.b64decode, code.replace(repl, ''), atob_count)
            video_sources = extract_source_tags(content)

            if not video_sources:
                soup = self.make_soup(content)
                for frame in soup.select('iframe'):
                    self.submit_parse_result(index_page_title=ttl,
                                             link_url=frame['src'],
                                             )
            else:
                for src in video_sources:
                    self.submit_parse_result(index_page_title=ttl,
                                             link_url=src[1],
                                             link_quality=src[0]
                                             )

    def _parse_parse_page(self, soup):
        # Actual video is a few pages down.
        # Click 'Tittu Nu' - watch now.
        # Follow embed link from there
        # Then extract from JS.
        watch_now = soup.find('a', 'btn_watch_detail')
        if watch_now and 'loading.swefilm' not in watch_now['href']:
            for watch_now_soup in self.soup_each([watch_now['href'], ] + [a.href for a in soup.select('.svep a')]):
                for iframe in watch_now_soup.select('iframe'):
                    if iframe['src'].startswith('http'):
                        for fsoup in self.soup_each([iframe['src'], ]):

                            page_title = ''
                            try:
                               page_title = fsoup.title.text.strip()
                            except AttributeError:
                                pass
                            tries = 0
                            while '404' in page_title and tries < 3:
                                tries += 1
                                time.sleep(15)
                                for fsoup in self.soup_each([iframe['src'], ]):
                                    page_title = ''
                                    try:
                                        page_title = fsoup.title.text.strip()
                                    except AttributeError:
                                        pass

                            self._submit_parses_from_soup(
                                fsoup,
                                ttl=self.util.get_page_title(soup)
                            )


class SeFilmNet(SweFilmTv):
    BASE_URL = 'http://sefilmdk.com'

    OTHER_URLS = ['http://sefilm.net', ]

    LONG_SEARCH_RESULT_KEYWORD = '300: Rise of an Empire'
    SINGLE_RESULTS_PAGE = True

    # Ugly workaround for parent structure.
    def get(self, url, **kwargs):
        return super(SeFilmNet, self).get(url, **kwargs)

    def _fetch_no_results_text(self):
        return 'Ingen oplysninger!'

    def _fetch_search_url(self, search_term, media_type):
        return u'%s/searche/%s' % (
            self.BASE_URL, self.util.quote(search_term.encode('utf-8')))

# http://player.swefilm.tv/player/player.php?data=V2xjMWFtSXlVbXhZTTFaNlZVZFdWVnB0ZUd0TlF6bG9WRmMwTW1ScVVqVlphMUo1VWxVNE1WUldXazlVTTNCeFpFaGFiMVV4WjNaUmFsWlhZakpXYTFNd1pHeFZWWEJoVEROWk5GSXphSEpVTURWVlkxUldlR0pYZUUxUFZXeENUVlJXZDB4NlZteFdNMHBCVGtSc01GVjZTa1JXVmtaeFYxWldNMUZyY0ZwUlIyUkxVakphZGxZd1VrUlVhMFpEVFVWQk5VNVlhRzFTUlVJMFpWVndkV013T0haa01VNHpVMnBTUVZOR1VUVmtWbVJKVFZka1JHTXdUbTFsYkdoMVZFWndXV1ZIYUc1UmJXODFUVVUxTWxWc1RtOVBWa3BRVFZSU1VVMUVVbkJOTTFaVllXMVdiVlpZVGxsa1IwcGhWbFZXZW1KcVRsbGtSV3N4VlVac2RXUXlSalJaVjNjMVVVZFpNMUp0V20xYWJWSlhZMFJHTTFGV1ozbFdNakYyWWtSU2RWcFlZekZrUjA1SFdteEpNbEpYVG5KU1ZVNXhZVmhDZFdGRk5WZGxXRTEyWkdwa1ExWlhWa2xrUlU1RFlWWk5kbE5YZUV0bGJFMDBZVWhrYlZKR1dUSk9ha1oyVWpCS1YxUlZWalZTV0ZKVVQxVkNXbEo2U2t4YVZ6VldWbXRrVEZKdE1VUmplbFpKVW10YVIxSlZTa1ZoYWtaWVZtdGtXbE5zWkVsVlZrb3hWVVZLTUZaR1dsVlRSRXBKVlZaR05GWkhaR3BTUldoVFVsWmFWRk5JUmsxU2JXUjZWbFZLU2xWclpGUk5NMDVGVVcxV2JWZHNXbEpYYkZKWFZHcFdlbUZ1YUV0VmExcFdZMFpPUWxGV2JFYz0=
