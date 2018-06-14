from sandcrawler.scraper import SimpleScraperBase

class ProgramasFullMega(SimpleScraperBase):

    BASE_URL = 'http://programasfullmega.com/'

    def setup(self):
        self.register_scraper_type(SimpleScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(SimpleScraperBase.MEDIA_TYPE_FILM)
        self.register_media(SimpleScraperBase.MEDIA_TYPE_TV)
        self.register_url(SimpleScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(SimpleScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'No hemos encontrado publicaciones'

    def _fetch_search_url(self, search_term, media_type):
        self.TERM = search_term
        return self.BASE_URL +'?s='+ '%s' % self.util.quote(search_term)

    def _fetch_next_button(self, soup):
         next = soup.select_one('div.older-entries a')
         if not next or not next['href']:
             return None

         return next['href']

    def _parse_search_result_page(self, soup):
        results = soup.select('div.article-title a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url= result['href'],
                link_title=result['title'].strip()
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.post-title').text

        for link in soup.select('table[class="tabla"] a[class="btn btn-mini enlace_link"]'):
            self.submit_parse_result(
                index_page_title= self.util.get_page_title(soup),
                link_url = link['href'].strip(),
                link_title=title
            )
