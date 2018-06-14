# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class MoviewatcherIo(SimpleScraperBase):
    BASE_URL = 'https://moviewatcher.is'
    OTHER_URLS = ['http://moviewatcher.is', 'http://moviewatcher.io']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    ALLOW_FETCH_EXCEPTIONS = True

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL +'/search?query=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Sorry! We could not find movies!'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next →')
        self.log.debug('------------------------')
        return self.BASE_URL + '/' + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('a.movie-title'):
            link = result
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)


        for link in soup.select('a.full-torrent1 div.play'):
            href = link['onclick']
            href = href.replace("window.open('",'').replace("')", '')
            if href.startswith('http'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=href,
                    link_title=link.text
                )
            elif href.startswith('/'):
                href = self.get_redirect_location(self.BASE_URL + href)
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=href,
                    link_title=link.text
                )
        for iframe in soup.select('div.players-section iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe['src'],
            )
