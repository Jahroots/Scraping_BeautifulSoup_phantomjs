# -*- coding: utf-8 -*-
import re
import time
import urllib
import base64
import json
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.videocapture import VideoCaptureMixin, extract_network_logs

START_FLAG = '<div class="bgf" id="bgf">'
END_FLAG = '<script data-cfasync="false" type="text/javascript" src="http://www.latinomovies.net/Temas/default/js/functions.js"></script>'


class LatinoMovies(SimpleScraperBase, VideoCaptureMixin):
    BASE_URL = 'http://www.latinomovies.net'
    OTHER_URLS = []

    # LONG_SEARCH_RESULT_KEYWORD = '2015'
    LONG_SEARCH_RESULT_KEYWORD = 'batman'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'esp'

        # self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        # self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        # self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        # self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self._request_size_limit = (1024 * 1024 * 60)  # Bytes

        self.requires_webdriver = ('parse',)
        self.adblock_enabled = False

    def _fetch_next_button(self, soup):
        if not hasattr(self, '_page_number'):
            self._page_number = 1
        for page in soup.select('ul.nav li a'):
            if page.text == str(self._page_number + 1):
                self._page_number += 1
                return self._base_search_url + '&page=%s' % (self._page_number)
        for page in soup.select('div.pagination ul li a'):
            if page.text == str(self._page_number + 1):
                self._page_number += 1
                return self._base_search_url + '&page=%s' % (self._page_number)

        return None

    #
    # def get_soup(self, url, **kwargs):
    #     # Broken html is breaking bs.
    #     # just return the main div... yuuuuuck
    #     result = self.get(url, **kwargs)
    #     content = result.content[
    #               result.content.find(START_FLAG):
    #               result.content.find(END_FLAG)
    #               ]
    #     return self.make_soup(content, url)

    def _fetch_search_url(self, search_term, media_type=None, page=1):
        self.start = page
        self.search_term = search_term
        self._base_search_url = self.BASE_URL + '/busqueda.php?q={}&page={}'.format(search_term.encode('utf-8'), page)
        return self._base_search_url

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup.text).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        if not soup.text.strip():
            return self.submit_search_no_results()
        if soup.text.strip() == u'\xab' + '1234567':
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

    def _parse_search_result_page(self, soup):
        for res in soup.select('div.mask'):
            link_title = unicode(res.h2.text.strip())
            link_url = res['onclick'].replace('location.href=', '').replace(';','').replace("'", '')
            link_url = self.util.canonicalise(self.BASE_URL,link_url)
            self.submit_search_result(
                    link_title=link_title,
                    link_url=link_url,
                    image = self.util.find_image_src_or_none(res, 'img')
            )

    def _fetch_no_results_text(self):
        return u'Ningún resultado para tu búsqueda'

    def parse(self, parse_url, **extra):
        resp = self.get(parse_url)

        use_webdriver = False
        dupes = set()
        soup = self.make_soup(resp.content)

        # Parse url page will contain following type of script tag in head part of HTML.
        # <script src="../../exes/rlvo.php?i=2089"></script>
        srch = re.findall('/([0-9]{0,4})/', parse_url)
        if not srch:
            raise ScraperParseException('Could not find pattern for rlvo.php')
        p_id = srch[-1]

        url = 'http://www.latinomovies.net/temps/get_links.php'
        prev_url = parse_url
        render_page = self.post(
            url=url,
            data={ 'p': p_id },
            headers={
                'Referer': prev_url,
                'X-Requested-With': 'XMLHttpRequest'
            }
        )

        #gkpluginsphp("linkl",{link:"xlmx*!c77!BeF0c!c77!c976Ly8x4b4D0onml!c96xlmx*Gllci5!c96b20vP2VyeG!BeFoxlmx*nFtY2c{707.v2x}"});
        #gkpluginsphp("linkc",{link:"xlmx*!c77!BeF0c!c77!c976Ly8x4b4D0onml!c96xlmx*Gllci5!c96b20vP2044b4D0onTNtY!c96Y1!c0324{707.v2x}"});

        srch = re.finditer(r'\{link\:\"(.*?)\"\}\)\;', render_page.content)
        if not srch:
            raise ScraperParseException('Could not find pattern for urls after fetching get_links.php')

        for match in srch:
            link_string = match.group(1)
            url = "http://www.latinomovies.net/views/ch_vd/plugins/gkpluginsphp.php"
            render_page = self.post(
                url=url,
                data={'link': link_string},
                headers={
                    'Referer': prev_url,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            )
            json_string = render_page.content
            srch = re.search(r'"link":"([^"]*)"', json_string)
            if srch:
                url = srch.group(1)
                url = url.replace('\\', '')
                if url not in dupes:
                    dupes.add(url)

        if dupes:
            for url in dupes:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup), link_url=url)
        else:
            use_webdriver = True
        if use_webdriver:
            self._parse_with_webdriver(parse_url, soup)


        # ------------------------------------------------------------------
        # ------- This part is for grabbing embedded player links ----------
        # ------------------------------------------------------------------

        # GET a URL based on that
        # http://www.latinomovies.net/exes/e.php?p=2437
        # http://www.latinomovies.net/exes/e.php?p=2089
        # http://www.latinomovies.net/exes/e.php?p=2436
        url = self.BASE_URL + '/exes/e.php?p=%s' % p_id
        resp = self.get(url)
        # var str = "
        srch = re.finditer(r'var\s*str\s*\=\s*\"(.*?)\"', resp.content)
        if not srch:
            raise ScraperParseException('Could not find pattern for rlvo.php')

        for match in srch:
            encoded_string = match.group(1)
            decoded_string = urllib.unquote(encoded_string)
            srch = re.search(r'src="([^"]*)"', decoded_string)
            if not srch:
                raise ScraperParseException('Could not find pattern for rlvo.php')
            url = srch.group(1)
            if "latinomovies" not in url:
                #self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=url)
                if url not in dupes:
                    dupes.add(url)
            # else:
            #     resp = self.get(url)
            #
            #     # ------------------------------------------------
            #     # This will contain
            #     # http://www.latinomovies.net/views/g_v.php
            #     # $.post("../../view/g_v.php", {i: "MTg0NQ=="},function(data){jQuery.globalEval(data);});
            #     # ------------------------------------------------
            #     srch = re.search(r'(\/view.*?)\"\,\s*\{i: \"(.*?)\"\}', resp.content)
            #     if not srch:
            #         raise ScraperParseException('Could not find pattern in g_v')
            #     prev_url = url
            #     url = srch.group(1)
            #     url = self.BASE_URL + url
            #     data_i = srch.group(2)
            #     data_n = "false"
            #     render_page = self.post(
            #         url=url,
            #         data={'i': data_i, 'n': data_n},
            #         headers={
            #             'Referer': prev_url,
            #             'X-Requested-With': 'XMLHttpRequest'
            #         }
            #     )

                # src="../../views/ch_vd/index.php?v=2603"
                # srch = re.search(r'(\/view.*?)\"', render_page.content)
                # if not srch:
                #     raise ScraperParseException('Could not find pattern in ch_vd')
                # prev_url = url
                # url = srch.group(1)
                # url = self.BASE_URL + url
                # render_page = self.get(url)
                #
                # # document.write(goin('UEdScGRpQnBaRDBpY0d4aGVXVnlNU0lnYzNSNWJHVTlJbmRwWkhSb09qUTNNSEI0TzJobGFXZG9kRG95TmpCd2VEdGlZV05yWjNKdmRXNWtMV052Ykc5eU9pTXdNREE3SUdScGMzQnNZWGs2SUdKc2IyTnJPeUJ3YjNOcGRHbHZianBoWW5OdmJIVjBaVHNnWW05MGRHOXRPakJ3ZURzZ2JHVm1kRG90TUhCNE95SStQQzlrYVhZK0NqeHpZM0pwY0hRZ2RIbHdaVDBpZEdWNGRDOXFZWFpoYzJOeWFYQjBJajRLWjJ0d2JIVm5hVzV6Y0dod0tDSndiR0Y1WlhJeElpeDdiR2x1YXpvaWVHeHRlQ29oWXpjM0lVSmxSakJqUkc5MlRETWhRbVZHYnpSaU5FUXdiMjVZTkdJMFJEQnZibkEwWWpSRU1HOXVSMVoyWTNrMU1DRmpNRE5wT1RNMFlqUkVNRzl1YlRGM1RtNXZlbGtoWXprMlRtc2hZemszV0VsMWVHeHRlQ29oWXpjM0lVSmxSblJpUVhzM01EY3Vkako0ZlhzM01EY3Vkako0ZlNKOUtUc0tQQzl6WTNKcGNIUSs='));
                # srch = re.search(r'goin\(\'(.*?)\'\)', render_page.content)
                # if not srch:
                #     raise ScraperParseException('Could not find goin pattern after ch_vd')
                #
                # encoded_string = srch.group(1)
                # decoded_string = urllib.unquote(base64.b64decode(base64.b64decode(encoded_string)))
                #
                # # gkpluginsphp("player1",{link:"xlmx*!c77!BeF0cDovL3!BeFo4b4D0onX4b4D0onp4b4D0onGVvcy50!c03i934b4D0onm1wNnozY!c96Nk!c97XIuxlmx*!c77!BeFtbA{707.v2x}{707.v2x}"});
                #
                # srch = re.search(r'\{link\:\"(.*?)\"\}\)\;', decoded_string)
                # if not srch:
                #     raise ScraperParseException('Could not find link pattern after ch_vd')
                #
                # link_string = srch.group(1)
                #
                #
                # prev_url = url
                # url = "http://www.latinomovies.net/views/ch_vd/plugins/gkpluginsphp.php"
                # render_page = self.post(
                #     url=url,
                #     data={'link': link_string},
                #     headers={
                #         'Referer': prev_url,
                #         'X-Requested-With': 'XMLHttpRequest'
                #     }
                # )
                #
                # srch = re.search(r'src=\\"([^"]*)\\"', render_page.content)
                # if not srch:
                #     raise ScraperParseException('Could not find pattern for embedded url in final step')
                # url = srch.group(1)
                # url = url.replace('\\','')
                # if url not in dupes:
                #     dupes.add(url)

        # ------------------------------------------------------------------
        # ------- This part is for grabbing download links -----------------
        # ------------------------------------------------------------------
        #
        # http://www.latinomovies.net/temps/get_links.php
        # Referer:http://www.latinomovies.net/pelicula/2437/escuadron-suicida.html
        # X-Requested-With:XMLHttpRequest
        # p=2437
        #



    def _video_player_ids(self):
        return ('video',)

    def _video_player_classes(self):
        return ()

    def _video_autoplay(self):
        return False

    def _trigger_container(self, container, driver, action='play'):
        if action == 'play':
            # sigh - shitty ads make for clicking 3 times to start it it.
            self._click_element(container, driver)
            time.sleep(5)
            self._clear_popups(driver)

        # Then our actual go time - play button is actually closer to the top.
        # and needs to be clicked... it's in an iframe, and the div is wonky!
        # iframe = container.find_element_by_tag_name('iframe')

        elementsize = container.size
        x_offset = elementsize['width'] / 2
        y_offset = elementsize['height'] / 3
        self._click_element(container, driver, x_offset=x_offset, y_offset=y_offset)

        if action == 'play':
            # And again...
            time.sleep(10)
            self._click_element(container, driver, x_offset=x_offset, y_offset=y_offset)

    def _get_video_containers(self, driver):
        containers = []
        for iframe in driver.find_elements_by_css_selector('div#video iframe'):
            if iframe.is_displayed():
                containers.append(iframe)
        return containers

    def _capture_video_logs(self, page_url, cleanup=True):
        # Overridden to skip through clicking each tab

        # Try and get browser from ScraperBase if present...
        driver = self.webdriver()

        driver.get(page_url)
        for link in driver.find_elements_by_css_selector('ul.nav ol a'):
            link.click()
            self._clear_popups(driver)
            containers = self._get_video_containers(driver)

            self.vcm_log.info("Found %d containers", len(containers))

            for container in containers:
                self.vcm_log.debug("Found container")
                if not self._video_autoplay():
                    self._trigger_container(container, driver)
                self.vcm_log.debug("Sleeping")
                time.sleep(self._video_wait_time())
                self.vcm_log.debug("Wake up")
                self._trigger_container(container, driver, action='stop')

        logs = extract_network_logs(driver)
        logs = self._filter_network_logs(logs)

        self.vcm_log.info("Found %d logs", len(logs))

        return logs

    def _parse_with_webdriver(self, parse_url, soup):
        # click each tab.
        for url in self._capture_video_urls(parse_url):
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup), link_url=url)
