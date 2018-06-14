#coding=utf-8

from sandcrawler.scraper import ScraperBase, OpenSearchMixin, ScraperAuthException


class ExcluziveNet(OpenSearchMixin, ScraperBase):
    BASE_URL = 'http://www.excluzive.net'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        # OpenSearchMixin advanced search settings
        self.bunch_size = 20
        self.media_type_to_category = 'film 10, tv 41'
        # self.encode_search_term_to = 'utf256'
        self.showposts = 0

    def search(self, search_term, media_type, **extra):
        self._login()
        super(self.__class__, self).search(search_term, media_type, **extra)

    def _login(self):
        login_url = 'http://excluzive.net'
        login_data = {}
        login_data.update(login_name='pilsner', login_password='Richard', login='submit')

        # Login first
        r = self.post(login_url, data=login_data)

        # We assume a valid login if these cookies are set; the site will delete them on failure
        if not all(key in r.cookies.keys() for key in ('dle_hash', 'dle_newpm', 'dle_password', 'dle_user_id')):
            raise ScraperAuthException("Login cookies not set")

    def _parse_search_result_page(self, soup):
        for link in soup.select('.indextitle a'):
            if not link.href.endswith('/films/'):
                self.submit_search_result(
                    link_title=link.text,
                    link_url=link.href
                )

    def parse(self, page_url, **extra):
        soup = self.get_soup(page_url)

        posts = soup.select('td.newsbody')
        for post in posts:
            links = post.select('a')

            for link in links:
                url = link.get('href')
                title = link.text
                if url:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=url, link_title=title)

            tokens = post.text.split()
            tokens = filter(lambda item: item.startswith("http"), tokens)
            for tok in tokens:
                self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=tok)
