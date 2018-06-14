# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilesPart(SimpleScraperBase):
    BASE_URL = "http://filespart.com"

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        raise NotImplementedError

    def _fetch_search_url(self, search_term, media_type):
        return '{}/{}/{}.html'.format(self.BASE_URL, search_term[0], search_term)

    def _fetch_no_results_text(self):
        return 'No results found'

    def _parse_search_result_page(self, soup):
        for result in soup.select(".vitem"):
            if result.select_one('.vdownload a'):
                self.submit_search_result(link_title=result.select_one('.viteminfo').text,
                                          link_url=result.select_one('.vdownload a').get('href'))

    def _fetch_next_button(self, soup):
        self.log.debug('----------------------')
        link = soup.select_one("#pagearea span")
        if link:
            next_page_link = [el for el in list(link.next_siblings) if el.name == 'a']
            if next_page_link:
                return self.BASE_URL + next_page_link[0]['href']

    def _parse_parse_page(self, soup):
        title = soup.select_one('.vdmaintitle h1').text
        for link in self.util.find_urls_in_text(soup.select_one('#vdtextarea textarea').text):
            if '...' not in link:
                # FIXME protected by captcha after sevaral requests :(
                # TODO so we need proxy rotator or Tor to catch all links
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_title=title,
                                         link_url=link)
