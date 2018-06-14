# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class StreamingkCom(SimpleScraperBase):
    BASE_URL = 'http://streamingk.com'
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(search_term)

    def _fetch_no_results_text(self):
        return u'Vous pouvez effectuer une nouvelle recherche ou utiliser les archives'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.nextpostslink')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.movief a'):
            link = result.href
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
                 )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for body in soup.select('div.filmicerik a'):
            for url in self.util.find_urls_in_text(unicode(body)):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url
                )
