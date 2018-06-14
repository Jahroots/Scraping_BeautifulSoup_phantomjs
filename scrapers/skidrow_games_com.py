# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SkidrowgamesCom(SimpleScraperBase):
    BASE_URL = 'https://www.skidrow-games.com'
    OTHER_URLS = ['https://www.skidrow-games.io', 'https://www.skidrow-games.com']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return u'No search results found, try searching again'

    def _fetch_search_url(self, search_term, media_type=None, page=1):
        self.start = page
        self.search_term = search_term
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL,  search_term=search_term, page=page)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup.text).find(no_results_text) >= 0:
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
        blocks = soup.select('div.post')
        for block in blocks[1:]:
            link = block.select_one('a')['href']
            title = block.text
            self.submit_search_result(
                link_url=link,
                link_title=title,
                image=self.util.find_image_src_or_none(block, 'img'),
            )


    def _parse_parse_page(self, soup):
            for link in soup.select('div.wordpress-post-tabs a[data-wpel-link="external"]'):
                index_page_title = self.util.get_page_title(soup)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text
                )