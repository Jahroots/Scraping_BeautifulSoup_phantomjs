# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class NukleoseriesCom(SimpleScraperBase):
    BASE_URL = 'http://www.nukleoseries.org'
    OTHER_URLS = ['http://www.nukleoseries.com']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    #def setup(self):
    #    raise NotImplementedError('The website is unreachable')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Sorry, but nothing matched your search criteria'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u"»")
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for results in soup.select('h2.post-title a'):
            if not results:
               return self.submit_search_no_results()
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div.entry iframe')
        for result in results:
            if 'image/gif' in result['src']:
                continue
            movie_link = result['src']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )
