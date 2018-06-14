# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class MegaFilmesHdNet(SimpleScraperBase):
    # BASE_URL = 'http://megafilmeshd.info'
    BASE_URL = 'http://megafilmeshd20.org'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "por"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for site in (self.BASE_URL, 'http://megafilmeshd.net', 'http://megafilmeshd.info'):
            self.register_url(ScraperBase.URL_TYPE_SEARCH, site)
            self.register_url(ScraperBase.URL_TYPE_LISTING, site)

    def _fetch_no_results_text(self):
        return 'NADA ENCONTRADO'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>>')
        if link:
            return link['href']

    def _parse_search_result_page(self, soup):
        for result in soup.select('a.absolute-capa.no-text.effect'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )

    def _parse_parse_page(self, soup):
        btn = soup.select_one('div.btn-flm')
        if not btn:
            return
        try:
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_title=soup.select_one('.t_arc').text,
                                     link_url=str(btn['onclick']).split('&v1=')[1].split('&')[0] or
                                              str(btn['onclick']).split('&v2=')[1].split('&')[0],
                                     )
        except:
            pass
