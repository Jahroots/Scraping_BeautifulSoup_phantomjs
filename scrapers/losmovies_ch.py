# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class LosMoviesCh(SimpleScraperBase):
    BASE_URL = 'http://los-movies.com'

    OTHER_URLS = [
        'http://losmovies.ac',
        'http://losmovies.io',
        'http://losmovies.es',
        'http://losmovies.me',
        'http://losmovies.ch',
        'http://losmovies.cc'
    ]

    LONG_SEARCH_RESULT_KEYWORD = 'home'
    SINGLE_RESULTS_PAGE = True



    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for site in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, site)
            self.register_url(ScraperBase.URL_TYPE_LISTING, site)

    def _fetch_no_results_text(self):
        return '0 movies found'  # this doesnt work

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search?type=movies&q=' + \
               self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        # No pagination apparent.
        return None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('div.showEntity div.showRowImage a'):
            image = result.find('img')
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=image['title'],
                image=image['src']
            )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        for link in soup.select('.linkTr .linkHidden.linkHiddenUrl'):
            url = link.text
            if url.find('http') == -1:
                url = 'http:' + url
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url= url,
                                     link_title= soup.select_one('.showRow.showRowNameWithYear.showRowText').text
                                     )
