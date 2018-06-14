# coding=utf-8

import re
import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SogouCom(SimpleScraperBase):
    BASE_URL = 'http://v.sogou.com'
    SINGLE_RESULTS_PAGE = True
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "zho"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)
        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'抱歉，没找到与“adfdsfasdf”相关的视频'

    def _fetch_next_button(self, soup):
        # Page numbers are calculated in javascript based on some in-page vars.
        page_search = re.search('var currentPageNum = (\d+)', str(soup))
        total_num_search = re.search('var totalNum = (\d+)', str(soup))
        href_search = re.search('var hrefBase = "([^"]*)";', str(soup))

        if page_search and total_num_search and href_search:
            page = page_search.group(1)
            total_num = total_num_search.group(1)
            href = href_search.group(1)
            # They escape ONE of them...
            href = href.replace('&amp;', '&')
            # Seems hard coded.
            number_per_page = 24

            last_page = (int(total_num) / number_per_page) + 1
            if int(page) == last_page:
                return None
            return self.BASE_URL + href + '&page=' + str(int(page) + 1)
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + \
            '/v?typemask=6&p=&dp=&w=06009900&_asf=&_ast=&dr=&enter=1&sut=1023&sst0=%s&query=%s' % (
                int(time.time()),
                self.util.quote(search_term)
            )

    def _parse_search_result_page(self, soup):

        results = soup.select('div.srch-container a.like-lst-tab')

        if not results and len(results) == 0:
            return self.submit_search_no_results()
        
        for result in results:
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.get('title', ''),
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _follow_link(self, link):

        if not link.startswith('http'):
            link = self.BASE_URL + link
        resp = self.get(link)
        # Check for a window.open('
        srch = re.search("window.open\(\\'(.*?)\\'", resp.content)
        if srch:
            return srch.group(1)

        self.log.info('Could not find link on %s', link)

        return link




    def _parse_parse_page(self, soup):
        page_title = soup.select_one('title')
        if page_title:
            index_page_title = page_title.text
        else:
            index_page_title = None

        a = soup.select('li.img-thumb a')

        for link in a:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=self.BASE_URL + link['href'],
                link_title=link['title'],
            )


        for link in soup.select('ul.drama_list li a'):
            link_url = self._follow_link(link['href'])
            if link_url:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link_url,
                    link_title=link.text,
                )

        for link in soup.select('ul.play_pg3 li a'):
            link_url = self._follow_link(link['href'])
            if link_url:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link_url,
                    link_title=link.text,
                )

        for link in soup.select('a.play_url'):
            link_url = self._follow_link(link['href'])
            if link_url:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link_url,
                    link_title=link.text,
                )

        for link in soup.select('ul.play_list2 li a'):
            link_url = self._follow_link(link['href'])
            if link_url:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link_url,
                    link_title=link.get('title', link.text)
                )


