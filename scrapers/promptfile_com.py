# coding=utf-8


from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase


class PromptFileCom(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://www.promptfile.com'
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        raise NotImplementedError('Deprecated. Website not available.')
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
        return super(PromptFileCom, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def parse(self, parse_url, **extra):
        self.submit_parse_result(index_page_title=self.util.get_page_title(self.get_soup(parse_url)),
                                 link_url=parse_url,
                                 )

