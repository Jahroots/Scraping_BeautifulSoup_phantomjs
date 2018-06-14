# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class VeryCdCom(SimpleScraperBase):
    BASE_URL = 'http://www.verycd.com'

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
        return u'抱歉！没有找到与'

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'next')
        if link:
            return self.BASE_URL + link['href']
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/entries/' + self.util.quote(search_term)

    def _parse_search_result_page(self, soup):
        for result in soup.select('ul#resultsContainer li.entry_item'):
            link = result.select('div.item_title strong.cname a')
            if link:
                self.submit_search_result(
                    link_url=self.BASE_URL + link[0]['href'],
                    link_title=link[0].text,
                    # image=self.util.find_image_src_or_none(result, 'img.cover_img')
                )

    def _parse_parse_page(self, soup):
        for link in soup.select('div.entry_video_list a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href']
                                     )
