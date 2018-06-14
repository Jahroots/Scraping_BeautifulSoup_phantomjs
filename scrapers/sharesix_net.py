# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.extras import SimpleGoogleScraperBase


class ShareSix(SimpleGoogleScraperBase):
    BASE_URL = 'http://www.sharesix.net'
    OTHER_URLS = []
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        raise NotImplementedError('the website is deprecated')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"


        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)

    def post(self, url, **kwargs):
        return super(self.__class__, self).post(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _parse_parse_page(self, soup):
        soup = self.post_soup(soup._url, data=dict(gotovideo=1))

        title = soup.title.text.replace('Download ', '').strip()
        embed = soup.select_one('#flvplayer embed')
        if embed:
            url = embed['flashvars'].split('file=')[1].split('&')[0]
            self.submit_parse_result(link_url=url,
                                     link_title=title,
                                     )
        elif "s1.addVariable('file','" in str(soup):
            # s1.addVariable('file','http://s1.sharesix.net/streams/42169.mp4?key=6798a94b6e2e52d47ce3c152cb13cdca');
            url = str(soup).split("s1.addVariable('file','")[1].split("')")[0]
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=url,
                                     link_title=title,
                                     )

    def parse(self, parse_url, **extra):
        self._parse_parse_page(
            self.get_soup(parse_url,
                          headers={'User-Agent': self.USER_AGENT, })
        )
