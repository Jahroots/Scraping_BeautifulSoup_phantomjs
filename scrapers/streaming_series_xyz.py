# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class StreamingSeriesXyz(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.seriestreaming.watch'
    OTHERS_URLS = [
        'http://www.streamingseries.biz',
        'http://www.seriestreaming.online',
        'http://www.streamingseries.biz',
        'http://www.streaming - series.info'
        'http://www.serie-streaming-tv.info',
        'http://www.streamingserie.info',
        'http://www.streaming-series.cc',
        'http://www.streaming-series.cx',
        'http://www.serie-streaming-tv.com'
    ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    REQUIRES_WEBDRIVER = True
    WEBDRIVER_TYPE = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'A la recherche des mots'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.movie-preview-content div.movie-poster a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for m_result in results:
            title = soup.find('h1').text

            self.submit_search_result(
                    link_url=m_result['href'],
                    link_title=title
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.find('h1').text.strip()
        movie_links = soup.select('div.video-container iframe')
        for movie_link in movie_links:
             link = movie_link['src']
             self.submit_parse_result(
                 index_page_title=index_page_title,
                 link_url=link,
                 link_text=title,
            )
