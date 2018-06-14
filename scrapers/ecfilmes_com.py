# coding=utf-8

from sandcrawler.scraper import SimpleScraperBase, ScraperBase


class EcFilmesCom(SimpleScraperBase):
    BASE_URL = 'http://www.ecfilmes.com'

    def setup(self):
        raise NotImplementedError('Website is out of reach')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "por"

        self.register_media(self.MEDIA_TYPE_FILM)
        self.register_media(self.MEDIA_TYPE_TV)

        self.register_url(
            self.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            self.URL_TYPE_LISTING,
            self.BASE_URL)

    def _parse_search_results(self, soup):
        if unicode(soup).find(u'Hay <b>0 </b> Resultados entre') >= 0:
            return self.submit_search_no_results()

        for result in soup.select('.imagen'):
            self.submit_search_result(
                link_url=result.a.href,
                link_title=result.a.text,
                image=result.img['src'],
            )

        next_button = soup.select_one('a.page.larger')
        if next_button and \
                ('/page/' not in soup._url or int(next_button.text) > int(soup._url.split('/')[4])) \
                and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button['href'])
            )

    def _parse_parse_page(self, soup):
        for iframe in soup.select('iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url='http:' + iframe['src'] if iframe['src'].startswith('//') else  iframe[
                                         'src'],
                                     )
