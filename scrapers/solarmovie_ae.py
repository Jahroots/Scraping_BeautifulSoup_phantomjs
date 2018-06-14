import base64
import urlparse

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.testrig import PassedTestException
from sandcrawler.scraper.caching import cacheable


class MerDB(SimpleScraperBase):
    BASE_URL = 'http://www.letmewatchthis.ac'
    OTHER_URLS = [
                  'http://www.letmewatchthis.li',
                  'http://merdb.mx',
                  'http://merdb.ae',
                  'http://merdb.club',
                  'http://www.letmewatchthis.one',
                  'http://www.letmewatchthis.pl',
                  'http://www.letmewatchthis.ltd',
                  'http://www.letmewatchthis.io'
                  ]


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL,] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self._request_connect_timeout = 500
        self._request_response_timeout = 600

    def get(self, url, **kwargs):
        return super(MerDB, self).get(url, allowed_errors_codes=[403, 522, ], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + "/?search_keywords=" + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return 'Sorry but I couldn\'t find anything like that'

    def _fetch_next_button(self, soup):
        link = soup.select_one('a[title="Next page"]')

        if link:
            return self.util.canonicalise(self.BASE_URL, link['href'])
        else:
            return None

    def _parse_tv_show_page(self, soup):
        # IMPROVE: Extract season and episode
        page_title = soup.title.text
        for result in soup.select('div.tv_episode_item a'):
            url = self.util.canonicalise(self.BASE_URL, result['href'])
            self.submit_search_result(link_title=(page_title + " " + result.text).strip(), link_url=url)

    def _parse_search_result_page(self, soup):
        for result in soup.select('.index_item.index_item_ie a'):
            url = result['href']
            if '/?genre=' in url:
                continue

            if '/tvshow/' in soup._url:
                for soup in self.soup_each([self.util.canonicalise(self.BASE_URL + "/tvshow/", url)]):
                    self._parse_tv_show_page(soup)
            else:
                self.submit_search_result(
                    link_url=self.util.canonicalise(self.BASE_URL, url),
                    link_title=result['title'].strip()
                )

    @cacheable()
    def _extract_link(self, url):
        qs = urlparse.parse_qs(url)
        if 'url' in qs:
            try:
                dec_url = base64.b64decode(qs['url'][0])
                if dec_url.startswith("http://"):
                    return dec_url
            except PassedTestException:
                pass
            except TypeError:
                pass
        # Try just following it.
        out_url = self.get_redirect_location(url)
        if out_url:
            return out_url
        return None

    def _handle_item_link(self, url, soup):
        url = self._extract_link(url)
        if url:
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=url
            )


    def _parse_parse_page(self, soup):
        for link in soup.select('.movie_version_link a'):
            url = link['href']

            if url.startswith("/goto.php?"):
                self._handle_item_link(self.util.canonicalise(self.BASE_URL, url), soup)
            else:
                # IMPROVE? Some links are to a "Sponsor Host" which requires login
                pass
