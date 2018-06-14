# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class SkidrowgamezNet(SimpleScraperBase):
    BASE_URL = 'https://skidrowgamez.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return u'Sorry, no posts matched your criteria.'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text='›')
        return next_link['href'] if next_link else None


    def _parse_search_result_page(self, soup):
        blocks = soup.select('figure.post-thumbnail')
        for block in blocks:
            link = block.select_one('a')['href']
            title = block.text
            self.submit_search_result(
                link_url=link,
                link_title=title,
                image=self.util.find_image_src_or_none(block, 'img'),
            )


    def _parse_parse_page(self, soup):
            for link in soup.select('div[class="entry-content clearfix"] a[class="external external_icon"]'):
                index_page_title = self.util.get_page_title(soup)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text
                )