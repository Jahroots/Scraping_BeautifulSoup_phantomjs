# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class Series4watchCom(SimpleScraperBase):
    BASE_URL = 'http://www.series4watch.online'
    OTHER_URLS = [
        'https://series4watch.tv',
        'http://www.series4watch.com',
        'http://www.series4watch.tv'
    ]

    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Nothing found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'الصفحة التالية «')
        if link:
           return link['href']

    def _parse_search_result_page(self, soup):
        find = 0
        for result in soup.select('div#ResultsAjax div.MovieBlock a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text,
            )
            find=1
        if not find:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        form = soup.select_one('div.MovieDetails form')
        soup = self.post_soup(
            form['action'],
            data={
                'watch': 1
            }
        )

        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div.downloadsList a[target="_blank"]')
        for result in results:
            movie_link = result['href']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
            )

        iframe = soup.select_one('iframe')
        if iframe:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe['src'],
            )
