#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class KinoFilmsTv(SimpleScraperBase):

    BASE_URL = 'http://kinofilms.me'
    OTHER_URLS = ['http://kinofilms.tv']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + \
            '/search/?genre=0&year_from=0&year_to=0&searchto=0&phrase=0' + \
            '&search=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Не найдено'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>>|')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('font.art-postcontent'):
            # Last link is text; first is image.
            links = result.select('a')
            image = links[0].find('img')['src']
            link = links[-1]
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=image,
            )

    def _parse_parse_page(self, soup):
        for iframe in soup.select('div.art-postcontent iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=iframe['src'],
                                     )

