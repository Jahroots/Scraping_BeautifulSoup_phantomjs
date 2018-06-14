#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class StreamCompletCom(SimpleScraperBase):

    BASE_URL = 'http://streamcomplet.me'
    OTHERS_URLS = ['http://streamcomplet.com']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "fra"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Essayer un autre mot'

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'nextpostslink')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.moviefilm'):
            img = result.find('img')
            link = result.select('div.movief a')[0]
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=img['src']
            )

    def _parse_parse_page(self, soup):
        for iframe in soup.select('div.filmicerik iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=iframe['src'],
                                     )

