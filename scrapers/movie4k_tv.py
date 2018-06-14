import re
import urlparse

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin


class Movie4KDotTv(CloudFlareDDOSProtectionMixin, ScraperBase):
    BASE_URL = 'https://movie4k.io'
    OTHER_URLS = ['https://movie4k.tv']
    SINGLE_RESULTS_PAGE = True
    TRELLO_ID = 'recqwzIkS'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        parsed = urlparse.urlparse(self.BASE_URL)
        withwww = '%s://www.%s' % (parsed.scheme, parsed.netloc)

        for url in (self.BASE_URL, withwww):
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/movies.php?list=search&search=' + self.util.quote(search_term)
        for soup in self.soup_each([search_url]):
            rows = soup.select('#tablemoviesindex tr')

            if not rows:
                return self.submit_parse_error('Could not find result rows', url=search_url)

            # If the site can't find the title, it will list a dummy item


            if soup.select_one('#tdmovies').text.lower().strip() == search_term.lower():
                return self.submit_search_no_results()

            if len(rows) == 1:
                links = rows[0].select('a')
                if not links or len(links) == 0 :
                    return self.submit_search_no_results()

                url = links[0].get('href')
                if url.startswith("http://ads") or url=='http://thepiratebay.to':
                    return self.submit_search_no_results()

            for row in rows:
                language = self._extract_language(row)

                links = row.select('a')

                page_links = []

                for link in links:
                    if link.select('img'):
                        continue

                    page_links.append(link)

                for link in page_links:
                    title = link.text.strip()
                    url = link.get('href')

                    if url.startswith('http://') and not url.startswith(self.BASE_URL):
                        continue

                    url = self.util.canonicalise(self.BASE_URL, url)

                    want_series_tag = media_type == ScraperBase.MEDIA_TYPE_TV
                    has_series_tag = u'(serie)' in title.lower() or u'(tvshow)' in title.lower()
                    if want_series_tag and not has_series_tag:
                        continue
                    if not want_series_tag and has_series_tag:
                        continue

                    self.submit_search_result(link_title=title,
                                              link_url=url,
                                              lang=language)

    def _extract_language(self, result_row):
        images = result_row.select('img')
        for img in images:
            src = img.get('src')
            m = re.match('/img/(.*)_(.*)_small.png', src)
            if m:
                parts = m.groups()
                if parts == ('us', 'flag'):
                    return "en"
                elif parts == ('us', 'ger'):
                    return "de"

    def parse(self, page_url, **extra):
        base_url = self.util.get_base_url(page_url)

        for soup in self.soup_each([page_url]):
            # extract link pages
            link_pages = soup.select('tr#tablemoviesindex2 a')

            link_page_urls = set()
            for page in link_pages:
                url = self.util.canonicalise(base_url, page.get('href'))
                link_page_urls.add(url)

            # Also try to extract out of javascript.
            # <a href=\"tvshows-1424225-Teen-Wolf.html\"
            for link in re.findall('<a href=\\\\"([^"|/]*\.html)\\\\"', unicode(soup)):
                url = self.util.canonicalise(base_url, link)
                link_page_urls.add(url)

            # remove this page as we have it already
            link_page_urls.discard(page_url)

            # crawl this page
            self._parse_link_page(soup)

            # crawl the rest
            for link_page in self.soup_each(link_page_urls):
                self._parse_link_page(link_page)

    def _parse_link_page(self, soup):
        # FIXME: There appears to be some obfuscation going on in Javascript
        # land... Not all links are scrapable via the HTML.

        content = soup.select('div#maincontent5')
        if not content:
            return self.submit_parse_error('Could not find content div')

        content = content[0]

        iframes = content.select('div iframe')
        for frame in iframes:
            width = frame.get('width')
            height = frame.get('height')

            if not width or not height:
                continue

            if self.util.looks_like_video_size(width, height):
                self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=frame.get('src'))

        ext_links = content.select('div a')
        for link in ext_links:
            img = link.find('img')

            # Not great :-(
            if img and img.get('src') == '/img/click_link.jpg':
                self.submit_parse_result(index_page_title=soup.title.text.strip(), link_url=link.get('href'))


class Movie4KTo(Movie4KDotTv):
    BASE_URL = 'https://movie4k.tv'
    OTHER_URLS = ['https://movie4k.to']

    def setup(self):
        #self.requires_webdriver = True
        #self.webdriver_type = 'phantomjs'
        raise NotImplementedError('duplicate of Movie4KDotTv')
        super(Movie4KTo, self).setup()


class Movie4KMe(Movie4KDotTv):
    BASE_URL = 'http://movie4k.me'

    def setup(self):
        raise NotImplementedError("Site no longer available.")


class MovieTo(Movie4KDotTv):
    BASE_URL = 'https://movie.to'

class Movie4kOrg( Movie4KDotTv):
    BASE_URL = "http://movie4k.org"

    def setup(self):
        super(Movie4kOrg, self).setup()

    def get(self, url, **kwargs):
        return super(Movie4kOrg, self).get(url, allowed_errors_codes=[521,], **kwargs)