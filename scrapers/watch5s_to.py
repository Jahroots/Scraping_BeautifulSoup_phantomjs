# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase, SimpleScraperBase,CloudFlareDDOSProtectionMixin
from sandcrawler.scraper import SimpleGoogleScraperBase, VideoCaptureMixin

import re



class Watch5sTo(SimpleGoogleScraperBase, VideoCaptureMixin, SimpleScraperBase):
    BASE_URL = 'https://watch5s.is'
    OTHER_URLS = ['https://watch5s.rs', 'http://watch5s.is', 'http://watch5s.com', 'http://watch5s.to']
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'


        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)

    def post(self, url, **kwargs):
        return super(self.__class__, self).post(url, verify=False, allowed_errors_codes=[404], **kwargs)


    def _fetch_no_results_text(self):
        return None


    def parse(self, parse_url, **extra):
        if '/watch/' not in parse_url:
            soup = self.get_soup(parse_url+'watch')
        else:
            soup = self.get_soup(parse_url)
        if '/tv-series/' in parse_url:
            for ep_links in soup.find_all('div', 'les-content'):
                for ep_link in ep_links.find_all('a'):
                    ep_soup = self.get_soup(ep_link['href'])
                    breadcrumb_text = ep_soup.find_all('span', itemprop='title')[-2].text + ' '+ ep_soup.find_all('span', itemprop='title')[-1].text
                    season, episode = re.findall('Season (\d+)', breadcrumb_text), re.findall('Episode (\d+)', breadcrumb_text)
                    if not season:
                        season = ''
                    else:
                        season = season[0]
                    if not episode:
                        try:
                            episode = re.findall('EP (\d+)', breadcrumb_text)[0]
                        except IndexError:
                            episode = ''
                    else:
                        episode = episode[0]

                    if '/watch/' not in ep_link['href']:
                        episode_link = ep_link['href'] + 'watch'
                    else:
                        episode_link = ep_link['href']
                    soup = self.get_soup(episode_link)

                    m = re.search(r'(embed_src:).*\"', soup.text)
                    if m and m.group(0):
                        url = 'http:' + m.group(0).replace('"', '').replace('embed_src:', '').strip()
                        self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                 series_season=season,
                                                 series_episode=episode,
                                                 link_url=url)
        if '/movie/' in parse_url:
            m = re.search(r'(embed_src:).*\"', soup.text)
            if m and m.group(0):
                url = 'http:' + m.group(0).replace('"', '').replace('embed_src:', '').strip()
                return self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=url)
