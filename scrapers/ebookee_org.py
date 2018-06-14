# coding=utf-8


from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase

class EBookeeOrg(SimpleScraperBase):
    BASE_URL = 'https://ebookee.org'

    def setup(self):

        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def get(self, url):
        return self.make_soup(super(self.__class__, self).get(url, verify=False).text)
        #return self.make_soup(page)

    def _fetch_no_results_text(self):
        return None

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?q=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        # Find the last li in the pagination.
        pagination_links = soup.select('div.pagination ul li a')
        if pagination_links and \
                        pagination_links[-1]['href'] != 'javascript:void()':
            return self.BASE_URL + pagination_links[-1]['href']
        return None

    def search(self, search_term, media_type, **extra):
        url = self._fetch_search_url(search_term, media_type)
        soup = self.get(url)
        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        found = False
        for result in soup.select('div#booklist li a'):
            found = True
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.text
            )
        if not found:
            self.submit_search_no_results()

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get(next_button)
            self._parse_search_result_page(soup)

    def parse(self, parse_url, **extra):
        soup = self.get(parse_url)
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        # Try and suck out the links as a hrefs, but fall back to just looking
        # for things that appear like links.
        links = set()
        link_titles = {}
        for link in soup.select('div#description a'):
            if link.get('href', None) is None:
                continue
            if link['href'].startswith('/go/'):
                link_url = link['href'][3:]
                links.add(link_url)
                link_titles[link_url] = link.text
            elif not link['href'].startswith('/'):
                links.add(link['href'])
                link_titles[link['href']] = link.text
        for link in self.util.find_urls_in_text(
                str(soup.select('div#description'))):
            links.add(link)
        for link in links:
            if not link.startswith('http'):
                # Some links to emails....
                continue
            self.submit_parse_result(
                link_url=link,
                link_title=link_titles.get(link, None),
                index_page_title=self.util.get_page_title(soup)
            )
