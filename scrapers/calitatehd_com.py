# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class CalitatehdCom(SimpleScraperBase):
    BASE_URL = 'http://calitatehd.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/{}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('ul.lista_filme h3 a'):
            result = results['href']
            title = results.text
            if not title:
                title = result.strip('/').split('/')[-1].replace('-',' ').split('full movie')[0]
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
        results = soup.select('div.continut_post p iframe')
        for result in results:
            movie_link = result['src']
            if 'http' not in movie_link:
                movie_link = 'http:'+movie_link
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )