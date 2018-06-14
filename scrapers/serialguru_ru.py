# coding=utf-8

from sandcrawler.scraper import ScraperBase,SimpleGoogleScraperBase

class SerialguruRu(SimpleGoogleScraperBase):
    BASE_URL = 'http://serialguru.ru'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self, *args, **kwargs):
        raise NotImplementedError('the website is offline')

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        scripts = soup.select('script')
        title = soup.select_one('meta[name="description"]')['content']
        if soup.text.find('"file":') > -1:
            text = soup.text.split('"file":')[1].split(' };')[0].replace('"','')
            self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=text,
                    link_title=title,
                )
