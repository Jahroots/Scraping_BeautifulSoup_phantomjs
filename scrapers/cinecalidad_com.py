from sandcrawler.scraper import SimpleScraperBase, SimpleGoogleScraperBase
from sandcrawler.scraper.caching import cacheable
class CineCalidad(SimpleGoogleScraperBase, SimpleScraperBase):
    BASE_URL = 'http://www.cinecalidad.to'
    #SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(SimpleScraperBase.SCRAPER_TYPE_OSP)
        self.register_media(SimpleScraperBase.MEDIA_TYPE_FILM)

        self.register_url(SimpleScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(SimpleScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'


    def _fetch_search_url(self, search_term, media_type):
        return 'https://www.google.com/search?q=' + \
               self.util.quote(search_term) + '+site:' + self.util.get_domain(self.BASE_URL)

    @cacheable()
    def _follow_obfuscation(self, url):
        self.webdriver().get(url)
        link = self.webdriver().find_element_by_css_selector('div#texto a')
        if link:
            return link.get_attribute('href')
        return None

    def parse(self, parse_url, **extra):
        wd = self.webdriver()
        wd.get(parse_url)
        index_page_title = self.util.get_page_title(self.make_soup(self.webdriver().page_source))

        # Clicking the simple links runs a 'hr' function over it - do that manually ;)
        results = wd.execute_script(
            """ return $('ul.linklist a').map(function(index, link) { return { link_url: hr(link), link_text: link.innerHTML } })""")
        for result in results:
            link_url = result['link_url']
            if link_url.startswith('/'):
                link_url = self.BASE_URL + link_url
            if link_url.startswith('http://adf.ly/8213384/'):
                link_url = link_url[22:]
            if link_url.startswith('http://www.cinecalidad.com/protect/v.html?i='):
                link_url = self._follow_obfuscation(link_url)

            if link_url:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link_url,
                    link_text=result['link_text']
                )
