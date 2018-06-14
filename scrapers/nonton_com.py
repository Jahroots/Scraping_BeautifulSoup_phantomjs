# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class NonTonDotCom(SimpleScraperBase):
    BASE_URL = "http://www.nonton.com"

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "ind"

        # NOTE: Requires indonesian proxy

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.proxy_region = 'idn'  # site can only be accessed in indonesia

    def _fetch_search_url(self, search_term, media_type):
        return "{0}/search/result/{1}".format(self.BASE_URL, self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Maaf, video tidak ditemukan!'

    def _parse_search_result_page(self, soup):
        results = soup.select("div.resultCont")
        if not results:
            return self.submit_search_no_results()

        for result in results:
            title = result.select_one('.result-title').text
            link = result.select_one("a")

            if link and title:
                self.submit_search_result(link_title=title,
                                          link_url=link.get('href'))

    def _fetch_next_button(self, soup):
        self.log.debug('----------------------')
        links = soup.select("ul.pagination li")
        if links:
            last_link = links[-1]
            if 'active' not in last_link['class']:
                link = last_link.select("a")
                if link:
                    return link[0]['href']

    def _parse_parse_page(self, soup):
        try:
            url = unicode(soup).split('  file:"')[1].split('",')[0]
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=url)
        except Exception as e:
            self.log.exception(e)
