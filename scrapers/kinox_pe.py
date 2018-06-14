# coding=utf-8

import time
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase, ScraperBase


class KinoxPe(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'https://kinox.pe'
    SINGLE_RESULTS_PAGE = True
    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/Search.html?q=' + \
               self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Keine Einträge vorhanden.'

    def _fetch_next_button(self, soup):
        link = soup.select('a#RsltTableStatic_next')
        if link:
            return link[0]['href']
        return None

    def _parse_search_result_page(self, soup):
        found = False
        for result in soup.select('td.Title a'):
            found = True
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text
            )
        if not found:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        season_selector = soup.find('select',
                                    attrs={'id': 'SeasonSelection'})
        if season_selector:
            for option in season_selector.select('option'):
                for episode in option['rel'].split(','):
                    episode_url = self.BASE_URL + \
                                  '/aGET/MirrorByEpisode/' + \
                                  season_selector['rel'] + \
                                  '&Season=' + option['value'] + \
                                  '&Episode=' + episode
                    self._parse_parse_page(
                        self.get_soup(episode_url),
                        {'series_season': option['value'],
                         'series_episode': episode,
                         'asset_type': ScraperBase.MEDIA_TYPE_TV
                         }
                    )
        else:
            self._parse_parse_page(soup, {})

    def _parse_parse_page(self, soup, kwargs):
        for li in soup.select('ul#HosterList li'):
            rel_link = self.BASE_URL + '/aGET/Mirror/' + li['rel']
            stream_json = self.get(rel_link).json()
            embed_soup = self.make_soup(stream_json['Stream'])
            for iframe in embed_soup.select('iframe'):
                kwargs['link_url'] = iframe['src']
                if 'http' not in kwargs['link_url']:
                    kwargs['link_url'] = 'http:' + kwargs['link_url']
                kwargs['link_title'] = stream_json['HosterName']
                self.submit_parse_result(self.util.get_page_title(soup), **kwargs)

            for link in embed_soup.findAll(['a', 'map', 'area']):
                if 'href' in link.attrs and link['href']:
                    kwargs['link_url'] = link['href'][8:] if link.href.startswith('/Out/?s=') else link.href
                    kwargs['link_title'] = stream_json['HosterName']

                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup), **kwargs)
