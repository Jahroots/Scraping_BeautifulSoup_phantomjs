# coding=utf-8

import json
import re
from sandcrawler.scraper import OpenSearchMixin, ScraperBase, SimpleScraperBase, UppodDecoderMixin


class KinoDomOrg(OpenSearchMixin, UppodDecoderMixin, SimpleScraperBase):
    BASE_URL = 'http://kino-dom.org'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    USER_AGENT_MOBILE = False

    def get(self, url, **kwargs):
        return super(KinoDomOrg, self).get(url, allowed_errors_codes=[404], **kwargs)

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div[class="post shortstory"] div[class="post info"] a'):
            link_url = result['href']
            if '.html' not in link_url:
                continue
            self.submit_search_result(
                link_url=result['href'],
                link_title=result.find_next('div', 'post-title').text.strip()
            )
            found=1
        if not found:
            self.submit_search_no_results()

    def decode_uppod(self, file_code):
            file_code = file_code[1:]
            uni_file_code = ''
            for i in range(0, len(file_code), 3):
                uni_file_code += '%u0' + file_code[i:i + 3]
            decoded_url =re.sub(r'%u([a-fA-F0-9]{4}|[a-fA-F0-9]{2})', lambda m: chr(int(m.group(1), 16)), uni_file_code)
            return decoded_url


    def _parse_parse_page(self, soup):
        script_text = soup.find('script', text=re.compile("pl:")).text
        result = re.search("""pl:\s?[\"|\'](.*)[\"|\']""", script_text)
        base = result.group(1).split('"')[0]

        links = soup.select('span[data-link]')
        for link in links:
            call_soup = self.get_soup(base + link['data-link'])
            track = call_soup.select('track')
            for t in track:
                self.log.debug(t)
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=t.select_one('location').text,
                    link_title=t.select_one('title').text
                )