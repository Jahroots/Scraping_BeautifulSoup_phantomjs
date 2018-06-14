# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class PelismegahdOrg(SimpleScraperBase):
    BASE_URL = 'https://www.pelismegahd.pe'
    OTHER_URLS = ['http://www.pelismegahd.pe']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('div.poster h2 a'):
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            found=1
        if not found:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        title = soup.select_one('h2.titulo a').text.strip()
        index_page_title = self.util.get_page_title(soup)
        result_text = soup.find(text='ENLACES PÚBLICOS').find_next('div').find_all('a')
        for result in result_text:
            movie_soup = self.get_soup(result['href'])
            for link in movie_soup.select('div#tab1 a'):
                movie_link = link['href']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_text=title,
                )
