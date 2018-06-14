# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.caching import cacheable

class MundoflvCom(SimpleScraperBase):
    BASE_URL = 'http://mundoflv.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Hay <b>0 </b> Resultados entre  189 películas disponibles'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Siguiente ›')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):

        for result in soup.select('li.s-item h3'):
            link = result.select_one('a')
            soup = self.get_soup(link.href)

            #get the serie ID and # seasons
            id = soup.select_one('div[data-nonce]')['data-nonce']
            num_seasons = len(soup.select('button.classnamer'))

            #get the chapter list
            for index in range(1, num_seasons + 1):
                soup = self.get_soup(self.BASE_URL + '/wp-content/themes/wpRafael/includes/capitulos.php?serie=' + id + '&sr=&temporada=' + str(index))
                chapters_num = len(soup.select('button.classnamer'))
                for i in range(1, chapters_num + 1):
                    self.submit_search_result(
                        link_url=self.BASE_URL + '/wp-content/themes/wpRafael/includes/enlaces.php?serie=' + id + '&temporada=' + str(index) + '&capitulo=' + str(i),
                        link_title=link.text,
                        image=self.util.find_image_src_or_none(link, 'img'),
                    )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('a[href*="exit.php?serv"]'):
            url = self.get_soup(link.href).select_one('meta[http-equiv="refresh"]')['content'].split('url=')[1]
            self.submit_parse_result(
                index_page_title = index_page_title,
                link_url = url,
                link_title = link.text,
            )
