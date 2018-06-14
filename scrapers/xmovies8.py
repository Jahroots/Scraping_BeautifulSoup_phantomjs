# coding=utf-8

from sandcrawler.scraper import SimpleScraperBase


class XMovies8(SimpleScraperBase):
    BASE_URL = 'http://xmovies8.tv'

    OTHER_URLS = ['http://xmovies8.ru',]

    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('the code needs to be finished')

        self.register_scraper_type(SimpleScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(SimpleScraperBase.MEDIA_TYPE_FILM)
        self.register_media(SimpleScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(self.URL_TYPE_SEARCH, url)
            self.register_url(self.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return 'Please send request to e-mail your questions'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>>')
        if link:
            return link['href']

    def _parse_search_result_page(self, soup):
        for result in soup.select('.tit a'):
            self.submit_search_result(
                link_url='http:'+result['href'],
                link_title=result.text.strip()
            )

    def _parse_parse_page(self, soup):

        sup = self.get_soup(soup._url + 'watching.html')

        for result in sup.select('.available-source'):
            sources_html = self.post(self.BASE_URL + '/goto/', data={'id': result['data-target']}).text
            # print sources_html
            # link = sources_html.split('document.location = "')[1].split('";')[0]

            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=result['data-url'],
                                     )
        # legacy code
        for result in soup.select('div.tab-content div.videoTabs iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=result['src'],
                                     )
