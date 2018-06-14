# coding=utf-8


from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class MovikiRu(SimpleScraperBase):
    BASE_URL = 'http://www.moviki.ru'
    LONG_SEARCH_RESULT_KEYWORD = '2015'


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

        self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Данный список пуст'

    def _fetch_search_url(self, search_term, media_type, start=1):
        self.start = start
        self.search_term = search_term
        self.media_type = media_type
        return self.BASE_URL + '/search/' + self.util.quote(search_term) +'/'


    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, self.media_type, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        for link in soup.select('#list_videos_videos_list_search_result_items div.item'):
            result = link.select_one('a')
            if result:
                self.submit_search_result(
                        link_title=result.text,
                        link_url=result.href
                )

    def _parse_parse_page(self, soup):
        title = self.util.get_page_title(soup)
        wd = self.webdriver()
        wd.get(soup._url)
        soup = self.make_soup(wd.page_source)
        if u'Это личное видео' not in soup.text:
            video_link = soup.select_one('video.fp-engine')
            if video_link:
                video_link=video_link['src']
                hdr = {'Referer': soup._url}
                redirect_url = self.get_redirect_location(video_link, headers=hdr)
                if 'http' not in redirect_url:
                    redirect_url = 'http:'+redirect_url
                movie_link = self.get_redirect_location(redirect_url)
                self.submit_parse_result(
                        index_page_title=title.strip(),
                        link_url=movie_link
                )
