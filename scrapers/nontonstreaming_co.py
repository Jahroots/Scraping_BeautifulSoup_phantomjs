# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleGoogleScraperBase

class NontonstreamingCo(SimpleGoogleScraperBase):
    BASE_URL = 'http://www.nontonstreaming.co'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)

        for source in soup.select('video source'):
            src = source.get('src', None)
            if src:
                self.submit_parse_result(
                    link_url=src,
                )

        for link in soup.select('a.btn'):
            url = link.href
            if not url:
                continue
            if url.startswith(self.BASE_URL):
                continue
            if url == soup._url:
                continue

            if url.startswith('http://www.cogihot.info/get/'):
                cogi_soup = self.get_soup(url)
                for link in cogi_soup.select('a.btn'):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link.href,
                        link_title=link.text,
                    )
                continue

            # Otherwise just smack it out.
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                link_title=link.text,
            )


