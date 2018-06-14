# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, OpenSearchMixin

class FullStreamNu(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://full-stream.io'
    OTHER_URLS = ['http://full-stream.nu']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]
    USER_AGENT_MOBILE = False
    TRELLO_ID = 'i0aHJSwd'

    def get(self, url, **kwargs):
        return super(FullStreamNu, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.fullstream h3.mov-title'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h4.title-name')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        for link in soup.select('div.elink a'):
            url = ''
            if link:
                if 'http' in link.href:
                    url = link.href
                else:
                    url = link['onclick']
                    if url:
                        if 'http' not in url:
                            continue
                        url = re.search("'(.+)'", url).group(0).replace("'", "")
                if url:
                    self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=url,
                                link_title=link.text,
                                series_season=series_season,
                                series_episode=series_episode,
                    )
