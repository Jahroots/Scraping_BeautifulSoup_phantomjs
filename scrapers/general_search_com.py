# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable



class GeneralSearchCom(SimpleScraperBase):
    """
    Notes:
        This search will return results from generalfil_es.py as well.
        These will be handled by that scraper; this scraper should only handle
        the general-search.com parse urls.
    """

    BASE_URL = 'http://www.general-search.com'
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    # Note - this domain is returend as search results sometimes.  This is handled
    # in another module.
    #OTHER_URLS = ['http://www.generalfil.es']
    OTHER_URLS = []

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        for url in [self.BASE_URL, ]:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return 'Sorry, but nothing found.'

    def _fetch_search_url(self, search_term, media_type):
        self.log.debug(search_term)
        return self.BASE_URL + '/download/' + \
               self.util.quote(search_term.replace(' ', '-'))

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'next»')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div#search-result-exact h4 a[href]'):
            link = result['href'].startswith('http') and result['href'] or \
                   self.BASE_URL + result['href']
            if '.es' in link:
                continue

            self.submit_search_result(
                link_url=link,
                link_title=result.text,
            )


    @cacheable()
    def _follow_link(self, url):
        return self.get(url, allow_redirects=False).headers.get('Location', url)

    @cacheable()
    def _extract_iframe(self, url):
        results = []
        for redirectsoup in self.soup_each([url, ]):
            for iframe in redirectsoup.select('iframe'):
                results.append(iframe['src'])
        return results

    def _parse_parse_page(self, soup):
        # Find files with a redirect setup in the downloads block
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.file-info a'):
            if link['href'].startswith('/fileinfo/'):
                # Grab it and submit iframes
                for link_url in self._extract_iframe(self.BASE_URL + link['href']):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link_url
                        )
        # Find 'download-form' and it's action.
        for form in soup.select('form#download-form'):
            url = form['action']
            if url.startswith('/go/'):
                url = self._follow_link(self.BASE_URL + url)
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url = url
            )


