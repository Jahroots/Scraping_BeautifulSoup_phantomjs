# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class SeriesonlinehdOrg(SimpleScraperBase):
    BASE_URL = 'http://www.seriesonlinehd.org'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Existe 0'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'Seguinte ›')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        any_results = False
        for results in soup.select('div.imagen a'):
            result = results['href']
            title = results.find('span')['title']
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        results = soup.select('table.tab-ep-list td.ep-leg a')
        for result in results:
            movie_soup = self.get_soup(result['href'])
            for movie_link in movie_soup.select('ul.player-opcoes a'):
                link_soup = self.get_soup(movie_link['href'])
                for iframe_link in link_soup.select('iframe'):
                    self.submit_parse_result(
                        index_page_title=self.util.get_page_title(soup),
                        link_url=iframe_link['src'],
                        link_text=title,
                    )
