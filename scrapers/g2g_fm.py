# coding=utf-8
import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class G2GFm(SimpleScraperBase):
    BASE_URL = 'http://xpau.se'
    OTHER_URLS = [
        'http://cyro.se',
        'http://4do.fm',
        'http://g2g.fm',
        'http://4do.se',
        'http://g2g-fm.com',
        'http://dayt.se'
        ]
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?dayq=' + self.util.quote(search_term)

    def get(self, url, **kwargs):
        return super(G2GFm, self).get(url, **kwargs)

    def _fetch_no_results_text(self):
        return 'No results were found'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>')
        if link:
            return self.BASE_URL + link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('table.topic_table td.topic_head a'):
            self.submit_search_result(
                link_url=self.BASE_URL + '/' + result['href'],
                link_title=result.text,
            )

    def _parse_parse_page(self, soup):
        for iframe in soup.select('blockquote.postcontent > div > iframe'):
            if not iframe['src'].startswith(self.BASE_URL):
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=iframe['src'],
                                         )
        for link in soup.select('div#downsec a'):
            # Skip the id="suby" - subtitles link to forum.
            if 'id' in link.attrs and link['id'] == 'suby':
                continue
            # XXX
            # Some of these appear to be dodgy download an exe links.
            # Not sure how to ascertain which are legit, and which aren't.

            if not link['href'].startswith(self.BASE_URL) and link.startswith_http:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=link['href'],
                                         )
