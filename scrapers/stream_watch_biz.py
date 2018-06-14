# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class StreamWatchBiz(SimpleScraperBase):
    BASE_URL = 'http://www.stream-watch.info'
    OTHER_URLS = ['http://www.stream-watch.co', 'http://stream-watch.biz']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?ids={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"La recherche n'a retourn"

    def _fetch_next_button(self, soup):
        return None

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403], **kwargs)

    def _parse_search_result_page(self, soup):
        for results in soup.select('div.block div.short-poster a')+soup.find_all('select', id='ep'):
            if not results:
               return self.submit_search_no_results()
            try:
                result = results['href']
            except KeyError:
                option_results = results.find_all('option')[1:]
                for option_result in option_results:
                    result = option_result['value']
                    title = option_result.parent.find_previous('div', 'shortstory').text.strip()
                    self.submit_search_result(
                        link_url=result,
                        link_title=title
                    )
            title = results.text.strip()
            if 'Episode' in title:
                continue
            if result:
                self.submit_search_result(
                    link_url=result,
                    link_title=title
                )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        series_season, series_episode = self.util.extract_season_episode(title)
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('div#media-player a')
        for result in results:
            movie_link = result['href']
            if 'youtube' in movie_link:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
                series_season=series_season,
                series_episode=series_episode,
            )
