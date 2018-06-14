#coding=utf-8

from sandcrawler.scraper import ScraperBase

class EuroStreamingTV(ScraperBase):

    BASE_URL = 'https://eurostreaming.club'
    OTHER_URLS  =  []

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/?s=' + self.util.quote(search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        results = soup.select('li.post')
        if not results:
            return self.submit_search_no_results()
        for result in results:
            image = result.select('div.post-thumb img')[0]['src']
            link = result.select('div.post-content h2 a')[0]
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=image
            )

        next_button = soup.select('a.next')
        if next_button and self.can_fetch_next():
            next_link = next_button[0]['href']
            if not next_link.startswith(self.BASE_URL):
                next_link = self.BASE_URL + next_link
            self._parse_search_results(
                self.get_soup(next_link)
            )


    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        for result in soup.select('div.entry-content a'):
            add = True
            for bad_domain in ('wikipedia.org', 'telefilm-central',
                'eurostreaming.tv'):
                if result['href'].find(bad_domain) >= 0:
                    self.log.debug('Skipping %s link.', bad_domain)
                    add = False
            if not result['href'].startswith('http'):
                add = False
            if add:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=result['href'],
                                         link_title=result.text,
                                         )


