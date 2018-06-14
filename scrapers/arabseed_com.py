# coding=utf-8

import re
from urlparse import urlparse

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable
from sandcrawler.scraper.exceptions import ScraperFetchException
from sandcrawler.scraper.extras import CloudFlareDDOSProtectionMixin


class ArabSeed(SimpleScraperBase):
    BASE_URL = 'https://arabseed.tv'
    OTHERS_URLS = ['http://arabseed.tv', 'http://arabseed.com', 'http://www.arabseed.com']
    TRELLO_ID = 'R34aP4mQ'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'ara'

        self._request_connect_timeout = 800
        self._request_response_timeout = 800

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in self.OTHERS_URLS + [self.BASE_URL]:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)


    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[520], **kwargs)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='›')
        if link:
            return link['href']
        return None

    def search(self, search_term, media_type, **kwargs):
        self.get(self.BASE_URL)
        super(ArabSeed, self).search(search_term, media_type, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '?s={}'.format(search_term)

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('div.list-related ul li a'):
            found = 1
            try:
                soup = self.get_soup(result['href'])
                title = soup.find('title').text
                if '404' in title:
                    continue
            except ScraperFetchException:
                pass
            else:
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result.text,
                )
        if not found:
            self.submit_search_no_results()

    @cacheable()
    def follow_until_offsite(self, url):
        for soup in self.soup_each([url, ]):
            link = None
            links = soup.select('h1 a')
            if links:
                link = links[0]['href']
            else:
                # See if there is a h1 with a newwindow onclick...
                h1_with_onclick = soup.find('h1', onclick=True)
                if h1_with_onclick:
                    match = re.match("NewWindow\('(.*?)'", h1_with_onclick['onclick'])
                    if match:
                        link = match.group(1)

            if link:
                # If the link is relative, use the previous url.
                if not urlparse(link).netloc:
                    prev_url = urlparse(url)
                    link = prev_url.scheme + '://' + prev_url.netloc + '/' + link
                return self.follow_until_offsite(link)
            else:
                return url

    def _parse_parse_page(self, soup):
        # Find a link that matches the correct url...
        #view online
        href = soup.select_one('link[rel="shortlink"]')['href']
        id = href.split('p=')[1]
        self.log.warning(id)
        soup = self.post(self.BASE_URL + '/wp-content/themes/asd-takweed/functions/inc/single/movies/server.php', data = {'id': id}, headers={'X-Requested-With' : 'XMLHttpRequest'} )
        soup = self.make_soup(soup.text)
        for i in range(0, len(soup.select('div[data-key]'))):
            soup = self.post(self.BASE_URL + '/wp-content/themes/asd-takweed/functions/inc/single/server/film.php',
                             data={'id': id, 'type': 'normal', 'key': i}, headers={'X-Requested-With': 'XMLHttpRequest'})
            soup = self.make_soup(soup.text)
            iframe = soup.select_one('iframe')
            if iframe:
                self.submit_parse_result(index_page_title= self.util.get_page_title(soup),
                                    link_url=iframe['src'],
                                    link_text=soup.select_one('h3').text )

