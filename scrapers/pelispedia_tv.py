# coding=utf-8
import time
from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin

class PelispediaTv(CloudFlareDDOSProtectionMixin, DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'https://www.pelispedia.tv/'
    OTHER_URLS = ['http://www.pelispedia.tv']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'spa'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    REQUIRES_WEBDRIVER = True
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def parse(self, parse_url, **extra):
        if '/serie/' not in parse_url:
            wd = self.webdriver()
            wd.get(parse_url)
            time.sleep(8)
            wd.switch_to_frame(wd.find_element_by_xpath("//div[@id='player']//iframe"))
            soup = self.make_soup(wd.page_source)
            self._parse_parse_page(soup)
            soup = self.make_soup(wd.page_source)
            self._parse_parse_page(soup)
            wd.switch_to_default_content()
            wd.close()
        else:
            wd = self.webdriver()
            wd.get(parse_url)
            time.sleep(8)
            soup = self.make_soup(wd.page_source)
            self._parse_parse_page(soup)
            wd.close()


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div#botones a'):
            if 'Html6' in link.href or '/ver?' in link.href:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_title=link.text,
                series_season=series_season,
                series_episode=series_episode,
            )

        for ep_links in soup.select('li[class="clearfix gutterVertical20"] a'):
            ep_soup = self.get_soup(ep_links.href)
            series_season = series_episode = None
            title = ep_soup.select_one('div#player center')
            if title and title.text:
                series_season, series_episode = self.util.extract_season_episode(title.text)
            for iframe_link in ep_soup.select('div.repro iframe'):
                iframe_soup = self.get_soup(iframe_link['src'])
                for url in iframe_soup.select('div#botones a'):
                    if 'Html6' in url.href or '/ver?' in url.href:
                        continue
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=url.href,
                        link_title=url.text,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
