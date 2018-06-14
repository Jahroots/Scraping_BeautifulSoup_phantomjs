# coding=utf-8
import json
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class XemphimsoCom(SimpleScraperBase):
    BASE_URL = 'https://xemphimso.com'
    OTHER_URLS = ['http://xemphimso.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404, 403], **kwargs)

    def _fetch_search_url(self, search_term, media_type=None, page=1):
        self.start = page
        self.search_term = search_term
        return '{base_url}/tim-kiem/{search_term}/page-{page}.html'.format(base_url=self.BASE_URL,
                                                                            search_term=search_term,
                                                                            page=page)

    def _parse_search_results(self, soup):
        no_results_text = self._fetch_no_results_text()
        if no_results_text and unicode(soup.text).find(no_results_text) >= 0:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, page=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _fetch_no_results_text(self):
        return u'Không tìm thấy kết quả với từ khóa'

    def _parse_search_result_page(self, soup):
        for result in soup.select('a[class="th tooltip"]'):
            button_watch = self.get_soup(result.href).select_one('a.btn-watch')['href']
            if 'javascript' in button_watch:
                continue
            links = self.get_soup(button_watch).select('td.listep a')
            for link in links:
                self.submit_search_result(
                    link_url=link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        script_url = soup.find('div', id='player')
        if script_url:
            script_url = script_url.find('script', attrs={'src':re.compile('https://grab.xemphimbox.com/player.js.php')})
            if script_url:
                script_text = self.get(script_url['src'], headers={'Referer':soup._url}).text
                re_urls = re.search("""sources = (.*);""", script_text)
                if re_urls:
                    urls = json.loads(re_urls.groups()[0])
                    for url in urls:
                        link_title = str(url['label'])
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=url['file'],
                            link_title=link_title,
                            series_season=series_season,
                            series_episode=series_episode,
                        )
