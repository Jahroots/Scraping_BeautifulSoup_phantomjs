# coding=utf-8

import base64
import re

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class SeriesbangTo(SimpleScraperBase):
    BASE_URL = 'http://www.seriesbang.to'

    REQUIRES_WEBDRIVER = True
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP , ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]

    def setup(self):
        raise NotImplementedError('Deprecated. This website merged with pelis24.mobi.')
        super(self.__class__, self).setup()
        self._request_response_timeout = 300
        self._request_connect_timeout = 300

    def post(self, url, **kwargs):
        kwargs['allowed_errors_codes'] = [404, 403,]
        return super(SeriesbangTo, self).get(url, **kwargs)

    def get(self, url, **kwargs):
        kwargs['allowed_errors_codes'] = [404, 403,]
        return super(SeriesbangTo, self).get(url, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Nada encontrado'

    def _fetch_no_results_pattern(self):
        return u'Nada encontrado'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'»')
        return link['href'] if link else None

    def _parse_search_results(self, soup):
        for results in soup.select('div.box-peli h1 a'):
            self.submit_search_result(
                link_url=results['href'],
                link_title=results.text
            )

        no_results_pattern = self._fetch_no_results_pattern()
        if no_results_pattern and re.search(r'(?imsu)' + no_results_pattern, unicode(soup)):
            return self.submit_search_no_results()
        next_button_link = self._fetch_next_button(soup)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h2[class="post-title entry-title"]')
        if title:
            title = title.text.strip()


        urls = soup.select('a[href*="seriesbang.binbox.io"]')
        for a in urls:
            a = base64.decodestring(a['href'].split('/o/')[1])

            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=a,
                                     link_text = title)

        urls = soup.select('li.dows a')
        for a in urls:
            self.submit_parse_result(index_page_title=index_page_title,
                                     link_url=a['href'],
                                     link_text=title)

        urls = soup.select('#boxbang ul li a')
        for a in urls:
            if self.BASE_URL in a['href']:
                aux_soup = self.get_soup(a['href'])
                iframe = aux_soup.select_one('#videoplayer iframe[allowfullscreen]')
                if iframe:
                    self.submit_parse_result(index_page_title=index_page_title,
                                             link_url=iframe['src'],
                                             link_text=title)

                link = aux_soup.select_one('#box-coment a')
                if link:
                    self.submit_parse_result(index_page_title=index_page_title,
                                             link_url=link['href'],
                                             link_text=title)