# coding=utf-8
from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class Cineblog01Bz(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://www.cineblog01.wiki'
    OTHER_URLS = ['https://www.cineblog01.blue', 'https://www.cineblog01.black', 'https://www.cineblog01.blog', 'https://www.cineblog01.win']

    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'ita'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_ALL)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Ci spiace ma la tua ricerca non ha prodotto alcun risultato'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None


    def _parse_search_result_page(self, soup):
        for result in soup.select('div.post-title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        title=soup.select_one('h1').text.strip()
        movie_links = soup.select('div.session iframe')
        for movie_link in movie_links:
            if 'youtube' in movie_link['src']:
                continue
            movie_link = movie_link['src']
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=movie_link,
                                     link_title=title
                                     )