# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ImovieEs(SimpleScraperBase):
    BASE_URL = 'http://imovie.es'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = 'the'
    #SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Deprecated. Website no longer available')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        a = soup.select_one('ul.pagination li.active')

        results = soup.select('div.item a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            soup = self.get_soup(result.href)
            result = soup.select_one('div.icon-play a')

            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

        #pagination

        if a.next_sibling and self.can_fetch_next():
            a = a.next_sibling.select_one('a')

            if a:
                self.log.debug(a)
                self.log.debug('-----------------')
                soup = self.get_soup(a['href'])
                self._parse_search_result_page(soup)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('meta[property="og:title"]')['content']
        #VHSPlugins
        iframes = soup.select('div.player iframe')

        if iframes:
            for link in iframes :
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link['src'],
                    link_title=link.text,
                )
        elif soup.select('#VHSPlugins'):
            links = self.util.find_file_in_js(soup.select('script')[11].text)
            for link in links:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url= link.replace('\/', '/'),
                    link_title=title
                )
