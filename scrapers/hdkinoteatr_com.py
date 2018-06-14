# -*- coding: utf-8 -*-

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin, VKAPIMixin


class HDKinoteatrCom(OpenSearchMixin, SimpleScraperBase, VKAPIMixin):
    BASE_URL = 'http://www.hdkinoteatr.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in (self.BASE_URL, 'http://hdkinoteatr.ru'):
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

            # self.requires_webdriver = ('parse',)

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов.'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.shortstory'):
            img = result.select('div.img img')[0]
            link = result.select('div.story h3 a')[0]
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=self.BASE_URL + img['src'],
            )

    def get_movies(self, url):

        # print url
        soup = self.get_soup(url)

        t = re.findall('<h1 class="btl">(.+?)<span', str(soup))
        if not t:
            t = re.findall('<h1 class="btl">(.+?)</h1>', str(soup))
        _m = re.findall('<div id="vid">[^\b]+', str(soup))
        m = re.findall('makePlayer\(\'(.+?)\'\)', str(_m[0]))

        if m:
            m[0] = [t[0], m[0]]

        if not m:
            _k = re.findall('vkArr=(.+)\;', _m[0])

            for player in eval(_k[1]):
                if "file" in player and player["file"].startswith('http:'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_title=t[0],
                                             link_url=player["file"]
                                             )
            # print 'FULL->',
            # pp(_k)

            if '"file":' in repr(_k):
                # FULL->['data.videos',
                #  '[{"comment": "1 \xd0\xbf\xd0\xbb\xd0\xb5\xd0\xb5\xd1\x80", "file": "oid=199130307&id=481646115&hash=06ec0a6aa4d74293&hd=2"},
                #    {"comment": "2 \xd0\xbf\xd0\xbb\xd0\xb5\xd0\xb5\xd1\x80", "file": "http://moonwalk.cc/video/c4d77f918ba1e12a/iframe"}]']
                _h = eval(_k[1])  # json.loads(_k[0])

                # pp(_h)
                m = []
                for _p in _h:
                    if 'playlist' in _p:  # _p['playlist']:
                        for _u in _p['playlist']:
                            m.append([_u['comment'].replace('&lt;br&gt;', ' '), _u['file']])
                    else:
                        m.append([t[0] + ' [' + _p['comment'] + ']', _p['file']])

            else:
                # FULL->['data.videos', "'oid=-52758051&id=511677568&hash=015d500731f07836&hd=2'"]
                m.append([t[0] + ' [ccommentt]', eval(_k[1])])
        # print str(m)
        if m:
            for w in m:
                # g = re.findall('(^oid=)',m[0])
                # print str(w)
                if re.findall('(^oid=)', w[1]):
                    url = w[1].replace('amp;', '').replace(';', '')
                    # print url
                    g = re.findall('code=code.replace\(\/(\(oid=.+)\/g,(.+)\).replace\(\/(.+)\/g,', _m[0])
                    g1 = g[0][0].replace('&amp;', '&') + '([0-9a-z]+)'
                    g2 = g[0][2].replace('&amp;', '&') + '([0-9a-z&=]+)'
                    # r = re.findall('(oid=[0-9a-z-]+&id=)([0-9]{2})([0-9]{2})([0-9]+&hash=)([0-9a-z]{3})([0-9a-z]{3})([0-9a-z]+)',url)
                    # print g1
                    r = re.findall(g1, url)
                    # print str(r)
                    url = r[0][0] + r[0][2] + r[0][1] + r[0][3] + r[0][5] + r[0][4] + r[0][6]
                    # print '[=== '+url
                    # r = re.findall('(oid=[0-9-]{1})([0-9]{2})([0-9]{2})([0-9a-z&=]+)',url)
                    r = re.findall(g2, url)
                    url = r[0][0] + r[0][2] + r[0][1] + r[0][3]
                    url = 'http://vk.com/video_ext.php?' + url.replace('amp;', '')
                    # print '[=== ' + url
                    self.submit_parse_result(
                                             link_title=t[0],
                                             link_url=url
                                             )

                    soup = self.get_soup(url)  # , from_encoding="windows-1251")
                    # print soup
                    g = None
                    g = re.findall('url([0-9]+)\"', str(soup))
                    hd = 3
                    g.reverse()
                    for rec in g:
                        # print str(rec)
                        if (str(rec) == '240'):
                            hd = 6
                        elif (str(rec) == '360'):
                            hd = 1
                        elif (str(rec) == '480'):
                            hd = 2
                        elif (str(rec) == '720'):
                            hd = 3
                        # print '================+' + str(hd)
                        title = str(rec) + 'p ' + w[0]
                        if hd == 3:
                            title = str(rec) + 'p ' + w[0]
                        # print title, url + '&hd=' + str(hd)
                        self.get_movie(url, title)

    def get_movie(self, url, title):

        # print ')get_movie(', url
        soup = self.get_soup(url)  # , fromEncoding="windows-1251")

        av = 0
        for rec in soup.findAll('param', {'name': 'flashvars'}):
            # print rec
            for s in rec['value'].split('&'):
                if s.split('=', 1)[0] == 'uid':
                    uid = s.split('=', 1)[1]
                if s.split('=', 1)[0] == 'vtag':
                    vtag = s.split('=', 1)[1]
                if s.split('=', 1)[0] == 'host':
                    host = s.split('=', 1)[1]
                # if s.split('=', 1)[0] == 'vid':
                #     vid = s.split('=', 1)[1]
                # if s.split('=', 1)[0] == 'oid':
                #     oid = s.split('=', 1)[1]
                if s.split('=', 1)[0] == 'hd':
                    hd = s.split('=', 1)[1]
            host = host.replace('vk.me', 'vk.com')
            video = host + 'u' + uid + '/videos/' + vtag + '.360.mp4'
            if int(hd) == 3:
                video = host + 'u' + uid + '/videos/' + vtag + '.720.mp4'
            elif int(hd) == 2:
                video = host + 'u' + uid + '/videos/' + vtag + '.480.mp4'
            elif int(hd) == 1:
                video = host + 'u' + uid + '/videos/' + vtag + '.360.mp4'

            self.submit_parse_result(
                                     link_title=title,
                                     link_url=video
                                     )
            # print video

    def parse(self, parse_url, **extra):

        self.get_movies(parse_url)
        return



        # Use the web driver here - there is some dynamic javascript that
        #  will obfuscate the links - the obfuscation method is what's
        #  dynamic.  We could try dynamically porting the code/regexes, but...
        # nah.
        # Instead click each link.
        wd = self.webdriver()
        wd.get(parse_url)
        links = wd.find_elements_by_css_selector(
            'div#vid div#videowrapper')
        for link in links:
            link.click()
            # Then just dig the iframe out.
            iframe = wd.find_element_by_css_selector('div#video_wrapper iframe')
            if iframe:
                self._parse_link(iframe.get_attribute('src'))

    def _parse_link(self, link):
        if link.find('oid%3D') >= 0:
            # reference to api.vk
            # Suck out the oid id and hash from the link; this
            # actually squirrels down about 3-4 iframes, but we're
            #  teh smrt scraper
            m = re.search('oid%3D(.*?)%26id%3D(.*?)%26hash%3D(.*)%26',
                          link)
            if m:
                (oid, v_id, hash) = m.groups()
                for url in self._fetch_from_vk_api(
                        oid, v_id, hash
                ):
                    self.submit_parse_result(
                                             link_url=url
                                             )
        else:
            # It just gets embedded, so it's the link we want.
            self.submit_parse_result(
                                     link_url=link
                                     )
