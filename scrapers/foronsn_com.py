# coding=utf-8

from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase

class ForonsnCom(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://www.foronsn.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    LONG_SEARCH_RESULT_KEYWORD = 'curso'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    # the website returns a message "Our systems detect that you can be a spammer therefore you have been denied
    #  registration. If you think it is a mistake, please contact an administrator" after every registration trial
    #  even a real email uses.

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('table[style="clear: both; border-bottom-width: 0;"]')
        if title and title.select_one('td.thead').text.strip():
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result in soup.select('div.codeblock code'):
            movie_links = self.util.find_urls_in_text(result.text)
            for movie_link in movie_links:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_title=movie_link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        for link in soup.select('div.post_body a'):
            if 'http' in link.text:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link.text,
                    link_title=link.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )