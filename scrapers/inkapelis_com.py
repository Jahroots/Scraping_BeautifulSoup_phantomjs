# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class InkapelisCom(SimpleScraperBase):
    BASE_URL = 'https://www.inkapelis.com'
    OTHER_URLS = ['http://www.inkapelis.com/']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = ''
        try:
            link = soup.find('div', 'pagenavi').find_all('a')[-1]
        except AttributeError:
            pass
        self.log.debug('------------------------')
        if link:
            return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        any_results = False
        for results in soup.select('a.info-title'):
            result = results['href']
            title = results.find('h2').text.strip()
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        results = soup.select('a.btn')
        for result in results:
            movie_link = result['href']
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=movie_link,
                link_text=title,
            )
