# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import re
import json

class So1hdNet(SimpleScraperBase):
    BASE_URL = 'http://www.so1hd.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return u'{}/search.html?s={}'.format(
            self.BASE_URL, self.util.quote(search_term)
        )

    def _fetch_no_results_text(self):
        return u'No results'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('ul.pagination li a[rel="next"]')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.movies-list div.ml-item a'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )


    def _find_redirect(self, url, referer):
        return self.get_redirect_location(
            url,
            headers={'Referer': referer}
        )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        srch = re.search(
            'jwplayer\("mediaplayer"\).setup\(.*sources:(\[.*?\]).*\);',
            unicode(soup)
        )
        if srch:
            # There's a trailing comma which breaks json...
            video_info = json.loads(srch.group(1).replace(',]', ']'))
            for source in video_info:
                # Not type's are metadata records
                if 'type' in source:
                    redirected =self._find_redirect(
                        source['file'],
                        soup._url,
                    )
                    if redirected:
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=redirected,
                        )
