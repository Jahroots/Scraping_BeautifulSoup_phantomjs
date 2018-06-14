# coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class RapidSearchEngine(SimpleScraperBase):
    BASE_URL = "https://rapid-search-engine.com"
    OTHER_URLS = ['http://mp3db.ru','http://amaderforum.com', 'http://www.puzo.org']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for site in [self.BASE_URL] + self.OTHER_URLS  :
            self.register_url(ScraperBase.URL_TYPE_SEARCH, site)
            self.register_url(ScraperBase.URL_TYPE_LISTING, site)

    def _fetch_search_url(self, search_term, media_type):
        return (self.BASE_URL + '/index-s={}&ftype={}.html'.format(search_term,
            4 if media_type == self.MEDIA_TYPE_FILM else 0))

    def _fetch_no_results_text(self):
        return 'Nothing found, sorry'

    def _parse_search_result_page(self, soup):
        for result in soup.select('.infoline3 a.big'):
            self.submit_search_result(
                link_title=result.text,
                link_url=result.href)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next')
        self.log.debug('-----------------')
        return self.BASE_URL + link['href'] if link else None

    def _parse_parse_page(self, soup):
        # submit the actual links as parse results.
        try:
            title = (soup.select_one('.big2') or soup.select_one('.col-md-10 > h2')) .text
        except:
            return

        for link in soup.select('.reslink a'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_title=title,
                                     link_url=link['href']
                                     )
        # But throw the source url back up in the air as a search result -
        # if we have a matching module, we'll then parse it.
        source_link = soup.find(
            'a', {'title': 'Click here to visit the source site'})
        if source_link:
            self.submit_search_result(
                link_title=source_link.text,
                link_url=source_link.href,
            )
