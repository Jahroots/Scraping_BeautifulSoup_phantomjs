# coding=utf-8

import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmesOnline2Com(SimpleScraperBase):
    BASE_URL = 'http://www.filmesonline2.tv'
    PLAYER_URL = 'http://player.filmesonline2.tv'
    OTHER_URLS = [
        'http://www.filmesonline2.com',
        'http://filmesonline2.tv',
        PLAYER_URL
    ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"
        raise NotImplementedError('the domain is suspended')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def search(self, search_term, media_type, **extra):
        content = self.get(self._fetch_search_url(search_term, media_type)).content
        # Remove some bits that seem to mess badly with BS.
        content = re.sub('<div class="info-filme".*?info-filme-->',
                         '',
                         content,
                         flags=re.DOTALL)
        self._parse_search_results(self.make_soup(content))


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Conteúdo não disponível'

    def _fetch_next_button(self, soup):
        next_link = soup.select_one('a.nextpostslink')
        if next_link:
            return next_link.href
        return None


    def _parse_search_result_page(self, soup):
        found = False
        for result in soup.select('div.box-filme > a.thumb'):
            found = True
            image = self.util.find_image_src_or_none(result, 'img.wp-post-image')
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title'],
                image=image
            )
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        # Embedded on the page, no obfuscation, just easy :D
        index_page_title = self.util.get_page_title(soup)
        for iframe in soup.select('div.content iframe'):
            if iframe['src'].startswith(self.PLAYER_URL):
                response = self.get(iframe['src'])
                for result in re.findall(
                    "addiframe\('(.*?)'\)",
                    response.content,
                ):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=result,
                    )
            else:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe['src'],
                )
