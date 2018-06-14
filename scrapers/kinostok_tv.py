# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, UppodDecoderMixin
import re

class KinostokTv(UppodDecoderMixin, SimpleScraperBase):
    BASE_URL = 'http://kinostock.tv'
    OTHER_URLS = ['https://kinostok.tv']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[404], **kwargs)


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/video/search?title={}'.format(search_term)

    def _fetch_no_results_text(self):
        return None#u'ничего не найдено'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Следующая')
        return self.BASE_URL+next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('div.media-body h5'):
            movie_link = results.select_one('a')['href']
            self.submit_search_result(
                link_url=movie_link,
                link_title=results.text,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def decode_uppod(self, file_code):
            file_code = file_code[1:]
            uni_file_code = ''
            for i in range(0, len(file_code), 3):
                uni_file_code += '%u0' + file_code[i:i + 3]
            decoded_url =re.sub(r'%u([a-fA-F0-9]{4}|[a-fA-F0-9]{2})', lambda m: chr(int(m.group(1), 16)), uni_file_code)
            return decoded_url

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1')
        if title:
            title = title.text
        meta = soup.find('meta', content=re.compile('iframe'))
        if meta:
            soup = self.make_soup(meta['content'])

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=soup.select_one('iframe')['src'],
                link_text=title,
            )