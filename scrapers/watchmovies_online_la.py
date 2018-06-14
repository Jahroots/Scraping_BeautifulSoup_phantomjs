# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class WatchmoviesOnlineLa(SimpleScraperBase):
    BASE_URL = 'http://watchmovies-online.org'
    OTHER_URLS = ['http://watchmovies-online.is', 'http://watchmovies-online.la',]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, ], **kwargs)


    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u"»")
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('h2 a'):
            result = results['href']
            self.submit_search_result(
                    link_url=result,
                    link_title=results.text,
                )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h3').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div.play-btn a')
        for result in results:
            movie_link = ''
            try:
                movie_link = result['href']
            except KeyError:
                pass
            if movie_link:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_text=title,
                )