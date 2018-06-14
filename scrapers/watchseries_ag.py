# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CacheableParseResultsMixin
from sandcrawler.scraper.caching import cacheable


class WatchSeriesAg(CacheableParseResultsMixin, SimpleScraperBase):
    BASE_URL = 'https://watchseriesfree.to'
    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def setup(self):
        raise NotImplementedError('Deprecated, Our new domain is SeriesFree.to. ')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in self.BASE_URL,:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.long_parse = True
        self._request_response_timeout = 400
        self._request_connect_timeout = 300

    def get(self, url, **kwargs):
        return super(WatchSeriesAg, self).get(url, allowed_errors_codes=[404, ], **kwargs)

    def _fetch_no_results_text(self):
        return 'No results'

    def _fetch_no_results_pattern(self):
        return 'No\s*results'

    def _fetch_next_button(self, soup):
        links = soup.find('a', text= ' › ')#soup.select('ul.pagination a')
        if links:
            return self.BASE_URL + links.href
        else:
            return None
        #for link in links:
         #   if u'›' in link.text:
         #       return self.BASE_URL + link['href']

    def _fetch_search_url(self, search_term, media_type):
        if media_type == ScraperBase.MEDIA_TYPE_TV:
            return self.BASE_URL + "/search/" + self.util.quote(search_term)

    def _parse_search_result_page(self, soup):
        for result in soup.select('article.serie-details div.table a'):
            link_url = self.util.canonicalise(self.BASE_URL, result['href'])
            for soup in self.soup_each([link_url]):
                self._parse_series_page(soup)

    def _parse_series_page(self, soup):
        episodes = soup.select('div[itemprop="containsSeason"] ul.simple-list li[itemprop="episode"]')

        for item in episodes:
            item = item.select_one('a[itemprop="url"]')
            title_block = item.select_one('span.txt-ell')
            title = title_block and title_block.text or None
            if '/serie/' not in item['href']:
                self.submit_search_result(
                    link_title=title,
                    link_url=self.BASE_URL + item['href']
                )

    def _parse_parse_page(self, soup):

            links = soup.select('a.watch-btn')
            title = self.util.get_page_title(soup)
            urls = set()

            for link in links:
                urls.add(self.util.canonicalise(self.BASE_URL, link['href']))

            for url in urls:
                link = self._parse_interstitial(url)
                if link:
                    self.submit_parse_result(index_page_title=title, link_url=link)
                #else:
                    #self.submit_parse_error("Could not find OSP site link")

                    # if not urls:
                    #     self.submit_parse_error("Could not find links")

    @cacheable()
    def _parse_interstitial(self, url):
        for soup in self.soup_each([url]):
            link = soup.select_one('article[class*="serie-details"] a[class*="action-btn"]')
            if link:
                return link.href

class WatchTVSeriesDotSE(WatchSeriesAg):
    BASE_URL = "https://watchtvseries.se"

    def setup(self):
        raise NotImplementedError('Deprecated.Our new domain is SeriesFree.to. ')

class WatchTVSeriesVC(WatchSeriesAg):
    BASE_URL = 'https://watchtvseries.vc'

    def setup(self):
        raise NotImplementedError('Deprecated.Our new domain is SeriesFree.to. ')
