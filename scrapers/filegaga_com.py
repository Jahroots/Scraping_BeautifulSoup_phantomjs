# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FileGagaCom(SimpleScraperBase):
    BASE_URL = 'http://filegaga.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'
        raise NotImplementedError('The domain has expired')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'No results found'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?q=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='NEXT')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div#resultarea div.left_line div.img_box a'):
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.find('img')['alt'],
                image=self.util.find_image_src_or_none(result, 'img')
            )

    def _parse_parse_page(self, soup):
        textarea = soup.select('div.green_line_direct textarea')
        if textarea:
            for link in textarea[0].text.split('\n'):
                if link.strip():
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link.strip(),
                                             )
