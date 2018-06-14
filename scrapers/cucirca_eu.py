#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import SimpleScraperBase


class CucircaEu(SimpleScraperBase):
    BASE_URL = 'http://cucirca.eu'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'did not match any entries'

    def _fetch_next_button(self, soup):
        # XXX
        # This is what is SHOULD be, but the site doesn't work D:
        link = soup.find('a', 'next')
        if link:
            return link['href']
        return None

    def _extract_season_episode(self, text):
        match = re.search('Season (\d+) Episode (\d+)', text)
        if match:
            return match.groups()
        return None, None


    def _parse_search_result_page(self, soup):
        for result in soup.select('div.post'):
            link = result.select('h1.entry-title a')[0]
            season, episode = self._extract_season_episode(link.text)
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                series_season=season,
                series_episode=episode,
                asset_type=ScraperBase.MEDIA_TYPE_TV
            )

    def _parse_parse_page(self, soup):
        # First suck out the header so we can get season/ep
        title = soup.find('h1', 'post-title').text
        season, episode = self._extract_season_episode(title)
        # Javascript callouts to
        # http://www.cucirca.eu/getvideo.php?id=193507&nr=20&time=1429763089910
        # Where id and nr come from each links onclick
        # Doesn't look like time matters.
        for link in soup.findAll('a',
            attrs={'onclick': re.compile('^video\(')}):
            match = re.search('video\((\d+),(\d+),\d+\)', link['onclick'])
            if match:
                vid_num, vid_id = match.groups()
                video_soup = self.get_soup(
                    'http://www.cucirca.eu/getvideo.php?id=%s&nr=%s' %
                    (vid_id, vid_num)
                )
                for iframe in video_soup.select('iframe'):
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=iframe['src'],
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode,
                                             )
            else:
                raise ScraperParseException(
                    'Failed to parse video onclick: %s' % link['onclick'])

