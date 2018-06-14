# coding=utf-8

from sandcrawler.scraper import ScraperBase, \
    SimpleScraperBase, ScraperFetchException, CacheableParseResultsMixin

class SerialyczCz(CacheableParseResultsMixin, SimpleScraperBase):
    BASE_URL = 'http://www.serialycz.cz'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cze'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    ALLOW_FETCH_EXCEPTIONS = True

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u"Sorry, we couldn't find any results based on your search query"

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='« Older Entries')
        self.log.debug('------------------------')
        return link['href'] if link else None


    def _parse_search_result_page(self, soup):
        for result in soup.select('div.entry-thumbnails'):
            link = result.select_one('a')
            soup = self.get_soup(link.href)

            seasons = soup.select('span.nadpis a')
            if seasons:
                for season in seasons:

                    self.submit_search_result(
                        link_url=season.href,
                        link_title=season.text,
                        image=self.util.find_image_src_or_none(result, 'img'),
                    )
            else:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div a[class*="btn"]'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
            )
