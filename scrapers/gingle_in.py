# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import re


class GingleIn(SimpleScraperBase):
    BASE_URL = 'https://www.gingle.in'
    OTHERS_URLS = ['http://www.gingle.in']
    LONG_SEARCH_RESULT_KEYWORD = 'girls'
    #LONG_SEARCH_RESULT_KEYWORD = 'man'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        # Fetch two separate search pages.
        return ["{0}?q={1}".format(self.BASE_URL + '/movies/', self.util.quote(search_term)),
                "{0}?q={1}".format(self.BASE_URL + '/watch/', self.util.quote(search_term))]

    def _fetch_no_results_text(self):
        return None#'All Movies returned zero results'

    def _fetch_no_results_pattern(self):
        return r'All\s*Movies\s*returned\s*zero\s*results'

    def _fetch_next_button(self, soup):
        next_div = soup.find('div', 'pageselecter', text='Next')
        if next_div:
            self.log.debug('----------------')
            url = next_div.parent.get('href', None)
            if url:
                basesearch = self.BASE_URL
                if re.search(r'\/watch\?q\=',unicode(soup)):
                    basesearch = self.BASE_URL + '/watch/'
                elif re.search(r'\/movies\?q\=',unicode(soup)):
                    basesearch = self.BASE_URL + '/movies/'
                url = self.util.canonicalise(basesearch,url)
                return url
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.movieholder > a')+soup.select('a.innerlink')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for link in results:
            image = self.util.find_image_src_or_none(link, 'img')
            image = image and self.BASE_URL + image or None
            self.submit_search_result(
                link_url=self.BASE_URL + link['href'],
                link_title=link.get('title'),
                image=image,
            )
    def search(self, search_term, media_type, **extra):

        for soup in self.soup_each(self._fetch_search_url(search_term, media_type)):
            self._parse_search_results(soup)

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        index_title = self.util.get_page_title(soup)
        # two types of page - cater for both.
        for linkblock in soup.select('div.linkholder'):
            link = linkblock.find('a')
            link_title = linkblock.text
            link_title = re.sub(r'\s+',' ',link_title)
            link_title = link_title.strip()
            self.submit_parse_result(index_page_title=index_title,
                                     link_url=link['href'],
                                     link_title=link_title,
                                     )
        downloadlinks = (soup.find_all('a', {'title': 'Download in High Quality'}) or []) + \
                        (soup.select('#web-buttons-idjyhws td a') or [])
        for downloadlink in downloadlinks:
            # follow it!.
            downloadsoup = self.get_soup(downloadlink['href'])
            downloadlink = downloadsoup.find('a', text='direct link')
            if downloadlink:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=downloadlink['href']
                                         )
