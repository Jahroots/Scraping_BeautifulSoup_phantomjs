# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ZippymoviezCh(SimpleScraperBase):
    BASE_URL = 'https://www.zippymoviez.fun'
    OTHER_URLS = ['https://www.zippymoviez.top', 'https://www.zippymoviez.us', 'https://www.zippymoviez.co', ]
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_OTHER, ]
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[429, 522], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search/?q={search_term}&sortby=relevancy'.format(base_url=self.BASE_URL, search_term=search_term)


    def _fetch_no_results_text(self):
        return u'There were no results'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('li.ipsPagination_next a')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('a[data-linktype="link"]')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)




        for pre in soup.select('div.cPost_contentWrap pre'):
            for link in self.util.find_urls_in_text(unicode(pre)):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url= link,
                    link_title=title.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )

        for link in soup.select('div.cPost_contentWrap a'):
            if 'http' in link.text:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.href,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )