#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class AquiPelisNet(SimpleScraperBase):

    BASE_URL = 'https://aquipelis.net'
    OTHER_URLS = ['http://aquipelis.net']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'spa'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        # self.show_in_browser(soup)
        results = soup.select('ul.lista-search li')
        if not results:
            self.submit_search_no_results()
            return
        for result in results:
            link = result.select('h2.nome-resultado a')[0]
            image_soup = self.make_soup(result['title'])
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text.strip(),
                image=self.util.find_image_src_or_none(image_soup, 'img')
            )

    def _parse_parse_page(self, soup):
        self._parse_iframes(soup, 'div.embeds-video iframe')
        for link in soup.select('ul.download-lista li a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link['href'],
                                     )
