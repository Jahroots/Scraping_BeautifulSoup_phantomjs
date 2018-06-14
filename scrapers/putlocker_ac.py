# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, VideoCaptureMixin, CloudFlareDDOSProtectionMixin
import base64


class PutlockerAc(CloudFlareDDOSProtectionMixin, SimpleScraperBase, VideoCaptureMixin):
    BASE_URL =  'https://www1.putlocker.ac'
    OTHER_URLS = ['https://putlockerstv.ac', 'https://putlocker.my', 'https://123putlocker.org/', 'http://putlocker.ac/']
    TRELLO_ID = '3tkChRPI'


    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '?s={}'.format(self.util.quote(search_term))
        soup = self.get_soup(search_url)
        self._parse_search_results(soup)

    def _parse_search_results(self, soup):
        if unicode(soup).find(
            u'Not Found? Try link from below') >= 0:
            return self.submit_search_no_results()
        for result in soup.select('div.custom')[2:]:
            self.submit_search_result(
                link_url=result.find('a')['href'],
                link_title=result.find('h2').text
            )
        next_link = soup.find('a', text=u'»')
        if next_link and self.can_fetch_next():
            self._parse_search_results(self.get_soup(
                next_link['href']
            ))

    def _video_player_classes(self):
        return ('jwplayer', 'postTabs_divs')

    def _video_player_ids(self):
        return ('vplayer_wrapper',)

    def get_season(self, soup):
        meta_text = ''
        try:
            meta_text = soup.find('meta', attrs={'name': 'description'})['content']
        except TypeError:
            pass
        season = episode = ''
        if 'Season' in meta_text or 'Episode' in meta_text:
            season, episode = self.util.extract_season_episode(meta_text)
            yield season, episode
        yield season, episode

    def get_url(self, soup, parse_url):
        flash_urls = self._capture_video_urls(parse_url)
        for flash_url in flash_urls:
            seasons_data = self.get_season(soup)
            for season_data in seasons_data:
                season, episode = season_data[0], season_data[1]
                if season:
                    yield flash_url, season, episode
                else:
                    yield flash_url, season, episode
        for link in soup.select('div.table-responsive a'):
            url = link['href']
            if '/watch-download.html' in url or '/4k' in url:
                continue
            if 'external.php' in url:
                url = url.split('url=')[-1]
                url = base64.decodestring(url)
            seasons_data = self.get_season(soup)
            for season_data in seasons_data:
                season, episode = season_data[0], season_data[1]
                if season:
                    yield url, season, episode
                else:
                    yield url, season, episode

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        title = soup.select_one('div.title h2').text
        series_season, series_episode = self.util.extract_season_episode(title)
        iframes = soup.select('iframe[allowfullscreen]')
        for iframe in iframes:
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=iframe['src'],
                                     link_title=title,
                                     series_season=series_season,
                                     series_episode=series_episode
                                     )

        links = soup.select('table[class="easy-table easy-table-default "] tbody td a[href*="external"]')
        for link in links:
            url = link.href.split('url=')[1]
            url = base64.decodestring(url)
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=url,
                                     link_title=title,
                                     series_season=series_season,
                                     series_episode=series_episode
                                     )


