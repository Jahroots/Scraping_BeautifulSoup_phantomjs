# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class Media1fireCom(SimpleScraperBase):
    BASE_URL = 'http://media1fire.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return self.BASE_URL + '/{}-search-p{}.html'.format(search_term, start)

    def _fetch_no_results_text(self):
        return u'عفوا لم يتم العثور علي اي نتائج'

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next() and soup.select('div.img_subj_3 a'):
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        rslts = soup.select('div.img_subj_3 a')
        for result in rslts:
            link = result['href']
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('font')
        if title and title.text:
            title = title.text

        download_link  = soup.select_one('a[href*="download.media1fire"]')
        if download_link and download_link['href']:
            download_link = download_link['href']

            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_title=title,
                link_url=download_link
            )
