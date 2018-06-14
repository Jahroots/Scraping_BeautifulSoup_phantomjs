# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class SipeliculasCom(SimpleScraperBase):
    BASE_URL = 'http://www.sipeliculas.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/ver/{}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Error 404 - SiPeliculas.com'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Siguiente »')
        return self.BASE_URL+'/'+next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('h3 a'):
            self.submit_search_result(
                link_url=results['href'],
                link_title=results.text,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.titulo-h1').text
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.player_website iframe'):
            movie_link = link['src']
            if 'sipeliculas.com/repros/' in movie_link:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )
        results_a = soup.select('ul.opciones-tab  li a')
        results_b = soup.find('ul', 'opciones')
        if results_b:
            results_b = results_b.find_all('a')
        if results_a and results_b:
            for options_links in  results_a + results_b :
                if u'Más opciones' in options_links.text:
                    continue
                if not options_links.has_attr('id'):
                    continue
                
                option_id = options_links['id']
                data = {'acc':'ver_opc', 'f':option_id}
                option_link = self.post('http://www.sipeliculas.com/ajax.public.php', data=data).text
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=option_link,
                    link_text=title,
                )

