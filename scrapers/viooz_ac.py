# coding=utf-8

import re
import base64
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class VioozAc(SimpleScraperBase):
    BASE_URL = 'https://vzm.ag'
    OTHERS_URLS = ['http://viooz.ac']
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'No movie was found, try different keyword.'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search?s=t&q=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='&#8594;')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.films div.film'):
            link = result.select('span.title_list a')[0]
            self.submit_search_result(
                link_url=link['href'],
                link_title=link['title'],
                image=self.util.find_image_src_or_none(result, 'img')
            )

    def _parse_parse_page(self, soup):
        arg_list = {'index_page_title': self.util.get_page_title(soup)}
        self._parse_iframes(soup, 'div.tabContent iframe',**arg_list)
        self._parse_links(soup, 'div.tabContent a.new-window',**arg_list)
        self._parse_gkpluginsphp(soup)
        self._parse_list_links(soup)

    def _parse_list_links(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2.title_font')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        links = soup.select('div.contenu a.menu_categorie_item')
        for enc_link in links:
            if '/go/' in enc_link['href']:
                link = base64.decodestring(enc_link['href'].split('/')[-1])
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link,
                    link_title=enc_link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

    def _parse_links(self, soup, css_selector=None, **kwargs):
            if css_selector is None:
                css_selector = 'a'
            for a_tag in soup.select(css_selector):
                href = a_tag.get('href', None)
                if href:
                    if 'index_page_title' not in kwargs:
                        kwargs['index_page_title'] = ''
                        try:
                            kwargs['index_page_title'] = self.util.get_page_title(soup)
                        except:
                            pass

                    self.submit_parse_result(link_url='http:' + href if href.startswith('//') else href,
                                             **kwargs
                                             )

    def _parse_gkpluginsphp(self, soup):
        page_content = soup.contents
        page_content = soup.prettify()
        # ---------------------------------------------------------------
        # gkpluginsphp("player4",{link:"14507eef9fc634e0223f3535481993ccee6daafa3637266b3a832ffbd138ac5727afb921ea14ca2e51f9f725ec387d6a"});
        # http://viooz.ac/p9/plugins/gkpluginsphp.php
        # link=14507eef9fc634e0223f3535481993ccee6daafa3637266b3a832ffbd138ac5727afb921ea14ca2e51f9f725ec387d6a
        # {"link":"http:\/\/www.cloudy.ec\/v\/5a7957135437f","func":"ZnVuY3Rpb24oKXt2YXIgcmVzPSJlcnIiO3RyeXt2YXIgZmlsZT1kdGEuc3BsaXQoL2ZpbGU6XHMqIi8pWzFdLnNwbGl0KCJcIiIpWzBdO3ZhciBmaWxlaz1kdGEuc3BsaXQoL2tleTpccyoiLylbMV0uc3BsaXQoIlwiIilbMF07cmVzPSJmaWxlOlwiIitmaWxlKyJcIjtrZXk6XCIiK2ZpbGVrKyJcIiI7dmFyIGNpZD1kdGEuc3BsaXQoL2NpZDpccyoiLylbMV0uc3BsaXQoIlwiIilbMF07cmVzKz0iY2lkOlwiIitjaWQrIlwiIjt9Y2F0Y2goZSl7fW9ianBsdWdpbi5yZXNwb25zZT1yZXM7c2VuZERhdGFUb1N2KG9ianBsdWdpbik7fQ==","poscom":"p0","request":{"url":"http:\/\/www.cloudy.ec\/embed.php?id=5a7957135437f&autoplay=1","method":"GET","responseEscape":true},"requesttype":"flash"}
        # data=eyJsaW5rIjoiaHR0cDovL3d3dy5jbG91ZHkuZWMvdi81YTc5NTcxMzU0MzdmIiwicG9zY29tIjoicDAiLCJyZXNwb25zZSI6ImVyciJ9
        # ---------------------------------------------------------------

        index_page_title = self.util.get_page_title(soup)
        prev_url = self.BASE_URL
        for parse_url in soup.select('h2.title_font a'):
            parse_url = parse_url.get('href',None)
            if parse_url:
                prev_url = parse_url
        srch = re.finditer(r'\{link\W+([^"]*)\"\}\)\;', page_content)
        if not srch:
            return None

        for match in srch:
            link_string = match.group(1)
            url = "http://viooz.ac/p9/plugins/gkpluginsphp.php"
            render_page = self.post(
                url=url,
                data={'link': link_string},
                headers={
                    'Referer': prev_url,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            )
            json_string = render_page.content
            srch = re.search(r'\"link\W+([^"]*)\"', json_string)
            if srch:
                url = srch.group(1)
                url = url.replace('\\', '')
                if url:
                    self.submit_parse_result(link_url='http:' + url if url.startswith('//') else url,
                                             index_page_title = index_page_title )
