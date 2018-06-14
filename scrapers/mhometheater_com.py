# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class MhometheaterCom(SimpleScraperBase):
    BASE_URL = 'http://mhometheater.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'jap'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return 'Nothing Found'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.nextpostslink')
        if next_button:
            return next_button.href
        return None

    def _parse_search_results(self, soup):
        self._parse_search_result_page(soup)
        next_button_link = self._fetch_next_button(soup)
        if self.can_fetch_next() and next_button_link:
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        results = soup.select('article header.entry-header h1.entry-title a[rel="bookmark"]')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            if 'Nothing Found' in result.text:
                return self.submit_search_no_results()
            link = result#.select_one('a')
            if link and 'p=' not in link.href:
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
        for result in soup.select_one('iframe[id="ac1254832be"]').find_all_next('a')[1:]:
            if 'rank' in result.href or u'人気ブログランキング' in result.text or u'動画を見る' in result.text\
                or u'インフォブログランキング' in result.text:
                continue
            if not result.text:
                break

            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=result.href,
                link_title=result.text,
                series_season=series_season,
                series_episode=series_episode,
            )

    def get(self, url, **kwargs):
        return super(MhometheaterCom, self).get(url, allowed_errors_codes=[404, ], **kwargs)