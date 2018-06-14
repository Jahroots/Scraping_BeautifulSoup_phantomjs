# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class HdtvDodovaCom(SimpleScraperBase):
    BASE_URL = 'http://92tv.dodova.com'
    OTHER_URLS = ['http://hdtv.dodova.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'cha'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('The website is deprecated')

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, proxies={'http': 'http://144.217.80.25:3128'}, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Sorry, but nothing matched your search terms'

    def _fetch_next_button(self, soup):
        next = soup.select_one('a.next')
        if next:
            return next.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('article.loop-wrap h3.loop-title'):
            link = result.select_one('a')
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
        for result in soup.select('div.entry p a'):
            if 'http' not in result.href and result.href.startswith('./'):
                continue
            self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=result.href,
                    link_title=result,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        for result in soup.select('div.entry p iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=result['src'],
                link_title=result.text,
                series_season=series_season,
                series_episode=series_episode,
            )
