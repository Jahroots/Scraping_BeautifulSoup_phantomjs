# coding=utf-8

import json
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, OpenSearchMixin, FlashVarsMixin


class KinoMoovNet(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://kinomovie.online'
    OTHER_URLS = ['http://kinomoov.org', 'http://kinomoov.net', 'http://kinomoov.org']
    LONG_SEARCH_RESULT_KEYWORD = u'mother'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        # self.search_term_encoding = 'windows-1251'

    def _fetch_no_results_text(self):
        return u'<div class="berrors">'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.basebox'):
            if 'contbox' in result['class']:
                continue

            # First link in the heading
            link = result.select_one('.heading a')
            # first image in the content is a link to the big image.
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'a.highslide img')
            )


    def _parse_parse_page(self, soup):
        # Super easy this time :)
        for iframe in soup.select('iframe'):

            url = iframe['src']
            url = self._extract_link(url)

            if not url:
                continue

            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=url,
                                     )

    def _extract_link(self, url):
        if 'api.kinomoov.net' not in url:
            return url

        for soup in self.soup_each([url]):
            # Try to get embed iframe
            match = re.search('iframe src="(http.*?)" width=', unicode(soup))
            if match:
                return self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=match.group(1))

            # Otherwise try to get `file` frame flashvars
            match = re.search('flashvars = ({.*?})', unicode(soup))
            if match:
                obj = {}

                try:
                    obj = json.loads(match.group(1))
                    for key, value in obj.items():
                        if '%' in value:
                            value = self.util.unquote(value)
                            obj[key] = value
                except ValueError as err:
                    self.submit_parse_result("Could not parse flashvars json",
                                             url=url)

                file_url = obj.get('file')
                image = obj.get('poster')

                if url:
                    self.submit_parse_result(index_page_title=soup.title.text.strip(), embed_url=url, link_url=file_url,
                                             image=image)
                    return

        # No dice
        return url
