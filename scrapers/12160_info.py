# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class One2169(SimpleScraperBase):
    BASE_URL = 'https://12160.info'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], verify=False, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/video/video/search?q={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No results were found'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Next ›')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for results in soup.select('div.xg_list div.bd'):
            if not results:
               return self.submit_search_no_results()
            result = results.select_one('a')
            title = results.select_one('a.title').text
            self.submit_search_result(
                link_url=result.href,
                link_title=title,
                image=result.img['src']
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div.vid_container iframe')
        for result in results:
            movie_link = result['src']
            if 'http' not in movie_link:
                movie_link = 'http:'+movie_link
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )