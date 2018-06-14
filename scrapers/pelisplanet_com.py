# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class PelisplanetCom(SimpleScraperBase):
    BASE_URL = 'http://www.pelisplanet.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(PelisplanetCom, self).get(url, allowed_errors_codes=[404, 403], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No se han encontrado peliculas para'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('div#movie-list div.b > a'):
            result = results['href']
            title = results.find('h2').text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        for movie_link in soup.select('div#repro_area iframe'):
            redirect_soup = self.get_soup(movie_link['src'])
            redirect_link = redirect_soup.find('div', id='embed')
            if redirect_link:
                redirect_link = redirect_link.find_next('script').text.split("file:'")[-1].split("',")[0]
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=redirect_link,
                    link_text=title,
                )
        for movie_link in soup.select('div#tabsrepro a')[1:]:
            link = movie_link['rel'][0]
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link,
                link_text=title,
            )
