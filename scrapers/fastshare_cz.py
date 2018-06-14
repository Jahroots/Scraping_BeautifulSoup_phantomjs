# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, CloudFlareDDOSProtectionMixin
import re


class FastshareCz(SimpleScraperBase):
    BASE_URL = 'https://fastshare.cz'
    OTHERS_URLS = ['http://fastshare.cz']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "cze"
        #self.requires_webdriver = True
        #self.webdriver_type = 'phantomjs'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        """
        A two step search process.
        """
        body = self.get(
            u'{}/{}/s'.format(self.BASE_URL, self.util.quote(search_term))
        ).content
        srch = re.search("url: '(\/test\.php\?token=.*&limit=)", body)
        found = False
        if srch:
            url = u'{}{}'.format(self.BASE_URL, srch.group(1))
            soup = self.get_soup(url + '50')
            for video in soup.select('li div.video_detail a'):
                self.submit_search_result(
                    link_url=u'{}{}'.format(self.BASE_URL, video.href),
                    link_text=video.text,
                )
                found = True
        if not found:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        index_page_title = self.util.get_page_title(soup)
        title = soup.find('h3', 'section_title').text.strip()
        season, episode = self.util.extract_season_episode(title)
        for freelink in soup.select('div.speed-low a'):
            if not freelink.href or freelink.href == '#':
                continue
            link_url = self.get_redirect_location(u'{}{}'.format(self.BASE_URL, freelink.href))
            if link_url:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link_url,
                    link_title=title,
                    series_season=season,
                    series_episode=episode
                )
