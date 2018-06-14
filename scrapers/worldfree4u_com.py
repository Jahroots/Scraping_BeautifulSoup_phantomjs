# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class WorldFree4UCom(SimpleScraperBase):
    BASE_URL = 'https://www.worldfree4u.lol'
    OTHER_URLS = ['http://www.worldfree4u.com', 'http://www.worldfree4u.cc', 'http://www.worldfree4u.me/']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        raise NotImplementedError('domains are redirected to a blog')

        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)
            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?action=the_search_text&s=' + search_term

    def _fetch_no_results_text(self):
        return 'No posts found.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='« Older Entries')
        if link:
            return link['href']

    def _parse_search_result_page(self, soup):
        results = soup.select('.archive_post')
        if not results:
            self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result.find('a')['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        # Filter out some dumb ones, but
        for link in soup.select('.post_body a'):
            url = link['href']
            if url.startswith('http://www.imdb.com') or \
                    url.startswith('http://www.youtube.com') or \
                    url.startswith('mailto:') or \
                    url.startswith('//www.pinterest.com') or \
                    url.startswith('/'):
                continue
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=url
                                     )
