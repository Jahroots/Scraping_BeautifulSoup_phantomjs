# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class HdsolarmovieCom(SimpleScraperBase):
    BASE_URL = 'https://hdgomovies.com'
    OTHERS_URLS = ['http://hdsolarmovie.com']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    SINGLE_RESULTS_PAGE = True

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No results to show with'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Next »')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for results in soup.select('div[class="content csearch"] div.result-item div.title a'):
            if not results:
               return self.submit_search_no_results()
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.data h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('iframe[class="metaframe rptss"]')
        for result in results:
            movie_link = result['src']
            if 'youtube' in movie_link:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )