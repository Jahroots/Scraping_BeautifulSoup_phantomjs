# coding=utf-8

from sandcrawler.scraper import ScraperBase, ScraperParseException
from sandcrawler.scraper.extras import EmbeddedGoogleScraperBase


class PasteBinCom(EmbeddedGoogleScraperBase, ScraperBase):
    BASE_URL = 'https://pastebin.com'
    OTHERS_URLS = ['http://pastebin.com']
    SINGLE_RESULTS_PAGE = True
    NO_RESULTS_KEYWORD = 'hhhdddnnnHFEJRYFG746TU43GT'
    LONG_SEARCH_RESULT_KEYWORD = '2016'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def get(self, url, **kwargs):
        return super(PasteBinCom, self).get(url, allowed_errors_codes=[404, 403], **kwargs)

    def _fetch_search_url(self, search_term, media_type, start=None):
        url = 'https://www.googleapis.com/customsearch/v1element?key=AIzaSyCVAXiUzRYsML1Pv6RwSG1gunmMikTzQqY&rsz=filtered_cse&num=10&hl=en&prettyPrint=false&source=gcsc&gss=.com&sig=01d3e4019d02927b30f1da06094837dc&cx=013305635491195529773:0ufpuq-fpt0&cse_tok=AHL74MygSmUbc7Tq1m9hZfN0iYGD:1505580252137&sort=&googlehost=www.google.com&callback=google.search.Search.apiary848&nocache=1505580279334'
        url += '&q=%s' % self.util.quote(search_term)
        if start:
            url += '&start=%s' % start
        return url


    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            # Use the text area for rawness
            textarea = soup.find('textarea', 'paste_code')
            # Appears to get different content based on user agent; fall back
            #  to div.text
            if not textarea:
                self.log.debug('Could not find textarea; using div.text')
                textarea = soup.find('div', 'text')

            if not textarea:
                return
                raise ScraperParseException(
                    'Could not find textarea or div.')
            for link in self.util.find_urls_in_text(
                    textarea.text, skip_images=True):
                if '.jpg' in link or '.png' in link or 'api.' in link:
                    continue
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup), link_url=link)
