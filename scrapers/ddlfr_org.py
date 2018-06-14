# coding=utf-8
import base64
import urllib2
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin


class DdlfrOrg(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://ddlfr.pw'
    OTHERS_URLS = ['https://ddlfr.org']
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'fra'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


    def _fetch_no_results_text(self):
        return u'Unfortunately, site search yielded no results'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div[class="movie-img img-box pseudo-link"]'):
            self.submit_search_result(
                link_url=result['data-link'],
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        for link in soup.select('div.cp a'):
            if 'go.php?' in link['href']:
                movie_link = base64.decodestring(urllib2.unquote(link['href'].split('url=')[-1]))
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=movie_link,
                    link_title=title,
                )
        for link in soup.select('article.full-page a'):
            if 'http' in link or link.has_attr('target'):
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=link.href,
                    link_title=title,
                )
