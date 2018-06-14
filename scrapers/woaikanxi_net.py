# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class WoaikanxiNet(SimpleScraperBase):
    BASE_URL = 'http://woaikanxi.net'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Apologies, but no results were found.'

    def _fetch_next_button(self, soup):
        next_link=''
        try:
            next_link = soup.find('a', text=u'Next »')
        except AttributeError:
            pass
        if next_link:
            return next_link['href']

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('h2.entry-title a'):
            title = results.text
            self.submit_search_result(
                link_url=results['href'],
                link_title=title,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.entry-title').text
        index_page_title = self.util.get_page_title(soup)
        for links in soup.select('span.su-lightbox'):
            link = links['data-mfp-src']
            self.submit_parse_result(
                   index_page_title=index_page_title,
                   link_url=link,
                   link_text=title,
               )
