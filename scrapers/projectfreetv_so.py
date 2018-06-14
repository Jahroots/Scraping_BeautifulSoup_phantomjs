# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class ProjectFreeTV(SimpleScraperBase):
    BASE_URL = 'https://my-project-free.tv'

    OTHER_URLS = [
        'https://myprojectfreetv.net',
        'http://myprojectfree.tv',
        'http://project-free-tv.im',
        'http://projectfreetv.at',
        'http://projectfreetv.in',
        'http://projectfreetv.im',
        'http://projectfreetv.so',
        'http://www.free-tv-video-online.info',
        'http://project-free-tv.sx',
        'http://project-free-tv.ch',
        'http://project-free-tv.li', 'http://projectwatchfree.tv', 'http://project-free-tv.ag'
    ]

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL,] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def get(self, url, **kwargs):

        return super(self.__class__, self).get(url,  allowed_errors_codes=[404], **kwargs)

    def search(self, search_term, media_type, **extra):
        self.media_type = media_type
        for soup in self.soup_each([self._fetch_search_url(search_term, media_type)]):
            self._parse_search_results(soup)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + (
            '/search-tvshows/?free=') + self.util.quote(search_term)

    def _parse_search_results(self, soup):
        self._parse_search_result_page(soup)
        if self.media_type == self.MEDIA_TYPE_FILM:
            next_button_link = self._fetch_next_button(soup)
            if next_button_link and self.can_fetch_next():
                self._parse_search_results(
                    self.get_soup(
                        next_button_link
                    )
                )

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next ›')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('div[class="post-content box mark-links entry-content"] a'):
            if 'season' in result.href or '/free/' in result.href:
                soup = self.get_soup(self.BASE_URL + result.href)
                episodes = soup.select('table a[href*="episode"]')
                for link in episodes:
                    self.submit_search_result(
                        link_url=link.href,
                        link_title=link.text
                    )
            else:
                self.submit_search_result(
                    link_url= result['href'],
                    link_title=result.text
                )
            found = 1
        for result_img in soup.select('div#content a img'):
            result = result_img.parent
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.get('title', None),
                image=self.util.find_image_src_or_none(result, 'img')
            )
            found = True

        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        ttl = soup.find('title').text

        checked = set()

        for epis_link in soup.select('.alternate_color a'):
            if (not epis_link.get('href', '') or '/reclame/' in epis_link.get('href', '')
                or epis_link['href'] == '#'):
                continue
            # Don't re-do them as there's multiple links for each.
            if epis_link['href'] in checked:
                continue
            checked.add(epis_link['href'])

            if not 'http' in epis_link['href']:
                epis_link['href'] = self.BASE_URL + epis_link['href']
            epis_soup = self.get_soup(epis_link['href'])
            if epis_soup.find('input', value="Continue to video"):
                link = epis_soup.find('input', value="Continue to video").parent['href']
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link,
                                         link_title=ttl,
                                         )
                continue

            for link in epis_soup.select('.alternate_color.variousfont a'):
                sea, episode = self.util.extract_season_episode(ttl)
                if "/watch/?aff_id=" in link.get('href', ''):
                    href = link['href']
                    if not href.startswith('http'):
                        href = self.BASE_URL + href
                    watch_video_soup = self.get_soup(href)
                    ttl = watch_video_soup.select_one('h1').text

                    for iframe in (watch_video_soup.find('iframe') or []):
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=iframe['src'],
                                                 link_title=ttl,
                                                 series_season=sea,
                                                 series_episode=episode
                                                 )

                    link = watch_video_soup.find('input', value="Continue to video").parent['href']
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=link,
                                             link_title=ttl,
                                             series_season=sea,
                                             series_episode=episode
                                             )
                elif link.get('onclick'):
                    for lnk in self.util.find_urls_in_text(link['onclick']):
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=lnk,
                                                 link_title=ttl,
                                                 series_season=sea,
                                                 series_episode=episode
                                                 )
