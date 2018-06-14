# coding=utf-8
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class RadioflyWs(SimpleScraperBase):
    BASE_URL = 'http://www.radiofly.ws'
    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'circles'
    OTHER_URLS = []
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self._request_size_limit = (2048 * 2048 * 50)
        self._ignore_chunked_encoding_error = True

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def __buildlookup(self):
        lookup = {}
        side_bar = self.get_soup(self.BASE_URL).find('div', id="side_bar")
        if side_bar:
            side_bar_links = side_bar.find_all('a')
            for side_bar_link in side_bar_links:
                if ('filme' in side_bar_link['href'] or 'dublate' in side_bar_link['href'] or 'serial' in side_bar_link['href']) and 'Online Gratis' not in side_bar_link.text:
                    for mainsoup in self.soup_each([side_bar_link['href'],]):
                            imgs = mainsoup.find_all('img')
                            for img in imgs:
                                if img.has_attr('title'):
                                    lookup[img['title'].lower().strip()] = side_bar_link['href']
        return lookup

    def search(self, search_term, media_type, **extra):
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)
        any_results = False
        for term, page in lookup.items():
            if search_regex.match(term) or search_term in term:
                self.submit_search_result(
                    link_url=page,
                    link_title=term,
                )

                any_results = True
        if not any_results:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        if 'filme' in soup._url or 'dublate' in soup._url:
            imgs = soup.find_all('img')
            for img in imgs:
                if img.has_attr('title'):
                    previous_paragraph = img.find_previous('p')
                    if previous_paragraph:
                        for link in previous_paragraph.find_all('a'):
                            if '.srt' in link['href']:
                                continue
                            self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=link['href'],
                                link_title=link['href'],
                            )
        if '2013' in soup._url:
            imgs = soup.find_all('img')
            for img in imgs:
                if img.has_attr('title'):
                    previous_paragraph = img.find_previous('p')
                    if previous_paragraph:
                        next_paragraph = previous_paragraph.find_next('p')
                        if next_paragraph:
                            for link in next_paragraph.find_all('a'):
                                if '.srt' in link['href']:
                                    continue
                                self.submit_parse_result(
                                    index_page_title=index_page_title,
                                    link_url=link['href'],
                                    link_title=link['href'],
                                )
        if 'serial' in soup._url:
            imgs = soup.find_all('img')
            series_season, series_episode = None
            for img in imgs:
                if img.has_attr('title'):
                    title = img.find_previous('a').previousSibling
                    if title and title.text:
                        series_season, series_episode = self.util.extract_season_episode(title.text)
                    previous_paragraph = img.find_previous('p')
                    if previous_paragraph:
                        if previous_paragraph:
                            for link in previous_paragraph.find_all('a'):
                                if '.srt' in link['href']:
                                    continue
                                self.submit_parse_result(
                                    index_page_title=index_page_title,
                                    link_url=link['href'],
                                    link_title=link['href'],
                                    series_season=series_season,
                                    series_episode=series_episode,
                                )
