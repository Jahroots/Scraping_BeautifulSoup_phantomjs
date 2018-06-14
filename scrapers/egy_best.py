# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class EgyBest(SimpleScraperBase):
    BASE_URL = 'https://egy.best'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type=None, page=1):
        self.start = page
        self.search_term = search_term
        return '{base_url}/explore/?page={page}&q={search_term}&output_mode=movies_list'.format(base_url=self.BASE_URL,
                                                                                     search_term=self.util.quote(search_term),
                                                                                     page=page)

    def _fetch_no_results_text(self):
        return u'لم يتم العثور على أفلام.'

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup.text).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, page=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )


    def _parse_search_result_page(self, soup):
        for result in soup.select('a.movie'):
            link = result.href
            image = self.util.find_image_src_or_none(result, 'img')
            if image and image.startswith('//'):
                image = 'http:' + image
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
                image=image,
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('table.dls_table a[class="btn b dl"]'):
            url = link.href
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=link.text,
            )
