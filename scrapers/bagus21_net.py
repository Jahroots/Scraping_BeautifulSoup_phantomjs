# coding=utf-8

import base64
import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin


class Bagus21(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://bagus21.net'
    LONG_SEARCH_RESULT_KEYWORD = 'man'

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Deprecated.The domain has expired')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)


        self.search_term_language = "ind"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ]:  # + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    # def search(self, search_term, media_type, **extra):
    #     self.get(self.BASE_URL + '/search/' + self.util.quote(search_term) + '.html')
    #
    #     for page in xrange(1, 101):
    #         the_list = self.get('http://api.fakfap.com/s/{}/limit/20/id/{}'.format(search_term.encode('utf-8'), page),
    #                             headers=dict(Referer=self._fetch_search_url(search_term, media_type),
    #                                          Origin=self.BASE_URL)).json()
    #         if not the_list:
    #             if page == 1:
    #                 self.submit_search_no_results()
    #             break
    #
    #         for result in the_list:
    #             self.submit_search_result(
    #                 link_url=self.BASE_URL + '/' + result['link']+'.html',
    #                 link_title=result['judul'],
    #             )

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/' + self.util.quote(search_term) + '.html'

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('article.item-block'):
            link = result.select_one('a').href
            if 'http:' not in link:
                link='http:'+link
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _fetch_no_results_text(self):
        # Nothing specific to check for, so check for no results below.
        return u'Hasil pencarian Hhhdddnnn'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='Halaman Berikutnya >>')
        self.log.debug('------------------------')
        return next['href'] if next else None

    def _parse_parse_page(self, soup):
        title = soup.select_one('title').text.replace(' Subtitle Indonesia Streaming Movie Download - Bagus21.net',
                                                      '').replace('Nonton Film ', '')
        for lnk in soup.select('.server-info a.btn'):
            if 'http:' not in lnk.href:
                lnk='http:'+lnk.href
            url = self.get(lnk).url
            if 'link.layarkaca21.net' in url:
                url = base64.decodestring(url.split('/?dl=')[1])
            else:
                sup = self.get_soup(url)
                script_url_server_text = script_url_text = ''
                try:
                    script_url_text = sup.select_one('script[src="/mine.js"]').find_next('script').text
                except AttributeError:
                    try:
                        script_url_server_text = sup.select_one('script[src="//lk21tv.com/embed/embed.js"]').find_next('script').text
                    except AttributeError:
                        pass
                if script_url_text:
                    script_url = re.search("""check_url=\'(.*)\',""", script_url_text)
                    script_url = script_url.group(1)
                    sup = self.get_soup('http:' + script_url)
                    link = re.search("""movie_url=\s?\"(.*)\",""", sup.text).group(1)
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=link,
                                             link_title=title
                                             )
                else:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=url,
                                             link_title=title
                                             )
                if script_url_server_text:
                    script_server_url_codes = script_url_server_text.split('haplugin_load|')[-1].split("'")[0]
                    code = script_server_url_codes.split('|')[1]
                    b = script_server_url_codes.split('|')[0]
                    c = script_server_url_codes.split('|')[2]
                    sup = self.get_soup('http://lk21tv.com/embed/embed.php?code={}&b={}&c={}'.format(code, b, c))
                    links_script = sup.select('script')[-2].text
                    links = self.util.find_file_in_js(links_script)
                    for link in links:
                        if not '.png' in link:
                            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                     link_url=link,
                                                     link_title=title
                                                     )

        for lnk in soup.select('.server-item a'):
            lnk64 = lnk.href.split('dl=')[-1]
            if '?' in lnk64:
                continue
            url = base64.decodestring(lnk64)
            if 'http' in url:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=url,
                                         link_title=title
                                         )


class Nonton21(SimpleScraperBase):
    BASE_URL = 'http://nonton21.net'
    LONG_SEARCH_RESULT_KEYWORD = 'girl'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "ind"

        raise NotImplementedError('The website is out of reach')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ]:  # + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):
        # uses a third party search...
        json_data = self.get(
            u'http://api.fakfap.com/s/{}/limit/20/id/1'.format(search_term)
        ).json()
        if not json_data:
            return self.submit_search_no_results()
        self._extract_video(json_data)

        page = 2
        while self.can_fetch_next():
            json_data = self.get(
                u'http://api.fakfap.com/s/{}/limit/20/id/{}'.format(search_term, page)
            ).json()
            if not json_data:
                break
            self._extract_video(json_data)
            page += 1


    def _extract_video(self, json_data):
        # Then a standard url format...
        for video in json_data:
            self.submit_search_result(
                link_url=self.BASE_URL + '/film-{}-subtitle-indonesia.html'.format(video['link']),
                link_title=video['judul']
            )



    def _parse_parse_page(self, soup):
        title = soup.select_one('article li.last a[itemprop="url"]')

        # Extra the download link.
        for link in soup.select('span[class="fa-download"]'):
            if link.parent.href:
                url = str(link.parent.href)
                if url.find('http') == -1:
                    url = 'http:' + url

                if url == 'http://ceritamimpi.com/url//':
                    continue
                    
                self.submit_parse_result(
                            link_url= url,
                            link_title = title.text
                )


        #streaming
        results = soup.select('div.server-info a')
        for result in results:
            if result.href.find('?size') > -1:
                self.submit_parse_result(
                    link_url= soup._url + result.href,
                    link_title=title.text
                )

class FilmBagus21(SimpleScraperBase):
    BASE_URL = 'http://moviebaru21.com'
    OTHER_URLS = ['http://filmbagus21.space', 'http://filmbagus21.org']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Sorry, no film matched your criteria'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        blocks = soup.select('div.moviefilm > a')
        any_results = False
        for block in blocks:
            link = block['href']
            title = block.text
            self.submit_search_result(
                link_url=link,
                link_title=title,
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        series = soup.select('div.rbgw_part a')
        for ep_link in series:
            ep_link = ep_link['href']
            if '#respond' in ep_link:
                continue
            series_soup = self.get_soup(ep_link)
            movie_links = series_soup.select('div.filmicerik iframe')
            for movie_link in movie_links:
                movie_link = movie_link['src']
                if 'youtube' in movie_link:
                    continue
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_title=movie_link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        movie_links = soup.select('div.filmicerik iframe')
        for movie_link in movie_links:
            movie_link = movie_link['src']
            if 'http' not in movie_link:
                movie_link = 'http:' + movie_link
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_title=movie_link,
                series_season=series_season,
                series_episode=series_episode,
            )
        script_links_text = soup.select_one('div.filmicerik div')
        if script_links_text:
            script_links_text = script_links_text.find_next('script').text

            for script_link in self.util.find_file_in_js(script_links_text):
                if '.jpg' in script_link or '.png' in script_link or '.vtt' in script_link:
                    continue
                    if script_link:
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=script_link,
                            link_title=script_link,
                            series_season=series_season,
                            series_episode=series_episode,
                        )
