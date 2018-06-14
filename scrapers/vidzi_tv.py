# coding=utf-8
import jsbeautifier
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper.extras import SimpleGoogleScraperBase


class VidziTV(SimpleGoogleScraperBase):
    BASE_URL = 'http://vidzi.tv'
    OTHER_URLS = []
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Website become an OSP.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)




    def _parse_parse_page(self, soup):
        title = soup.title.text.replace('Watch ', '').strip()

        paccked = 'eval(' + str(soup).split('<script type="text/javascript">eval(')[1].split('</script>')[0]

        if paccked:
            pcontent = jsbeautifier.beautify(
                paccked)  # .replace('"', '\''))  # jsunpack.unpack(paccked[0].replace('"','\''))
            # print pcontent
            vidlink = re.compile('\{file:\s*"(.+?)\"').findall(pcontent)[0]
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=vidlink,
                                     link_title=title,
                                     )
            #
            #
            # if ".mp4" in str(soup):
            #     url = str(soup).split("\n		file: \"")[1].split('"')[0]
            #     self.submit_parse_result(index_page_title=soup.title.text.strip(),
            #                              link_url=url,
            #                              link_title=title,
            #                              )

    def parse(self, parse_url, **extra):

        self._parse_parse_page(
            self.get_soup(parse_url,
                          headers={'User-Agent': self.USER_AGENT, })
        )
