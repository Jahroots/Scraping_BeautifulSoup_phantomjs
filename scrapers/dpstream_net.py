# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase


class DPStreamNet(ScraperBase):
    BASE_URL = 'https://www.dpstream.net'
    OTHERS_URLS = ['https://www.dpstream.net']
    USER_AGENT_MOBILE = False

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "fra"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _details_from_url(self, url):
        # Tries to return (season, episode, lang) from a url.
        (season, episode, lang) = (None, None, None)
        search = re.search(
            'saison-(\d+)-episode-(\d+)-(\w+).html',
            url
        )
        if search:
            (season, episode, lang) = search.groups()
            season = int(season)
            episode = int(episode)
        return (season, episode, lang)

    def search(self, search_term, media_type, **extra):
        if media_type == ScraperBase.MEDIA_TYPE_TV:
            self._search_tv(
                self.get_soup(
                    self.BASE_URL + '/series-recherche?q=' + self.util.quote(search_term)
                )
            )
        else:
            self._search_film(
                self.get_soup(
                    self.BASE_URL + '/films-recherche?q=' + self.util.quote(search_term)
                )
            )

    def _search_tv(self, soup):
        found = False
        for series in soup.select('h3[class="resultTitle uppercaseLetter pull-left"] a'):
            for series_soup in self.soup_each([self.BASE_URL + '/' + series['href']]):
                title = series_soup.title.text
                for link in series_soup.select('table[class="table season-table"] a'):
                    (season, episode, lang) = self._details_from_url(link['href'])
                    if 'javascript' not in link['href']:
                        self.submit_search_result(
                            link_url= self.BASE_URL + link['href'],
                            link_title=(title + " " + link.text).strip(),
                            series_season=season,
                            series_episode=episode,
                            asset_type=ScraperBase.MEDIA_TYPE_TV
                        )
                    found = True
        if not found:
            self.submit_search_no_results()

    def _search_film(self, soup):
        found = False
        for link in soup.select('.resultTitle.uppercaseLetter.pull-left a'):
            self.submit_search_result(
                link_url=self.BASE_URL + link['href'],
                link_title=link.text.strip(),
            )
            found = True
        if not found:
            self.submit_search_no_results()

    def parse(self, parse_url, **extra):
        submitted = set()
        soup = self.get_soup(parse_url)
        season, episode = self.util.extract_season_episode(soup.title.text)

        for lnk in soup.select('td a[href*="external_link"]'):
            submitted.add(lnk.href)
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=lnk.href,
                                     link_title=soup.select_one('div.tv_titleststus').text,
                                     series_season=season,
                                     series_episode=episode,
                                     )

        for lnk in soup.select('.playerwrapnotlogged a'):
            submitted.add(lnk.href)
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=lnk.href,
                                     link_title=soup.select_one('.markerOrange.no-bold').text,
                                     series_season=season,
                                     series_episode=episode,
                                     )

        for iframe in soup.select('iframe'):
            if iframe['src'].startswith('http'):
                submitted.add(iframe['src'])
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=iframe['src'],
                                         series_season=season,
                                         series_episode=episode,
                                         )
        # Also check the sidebar for the matching episode links - this
        # is often lazy loaded.
        for watch_episode in soup.select('a.b'):
            if parse_url.endswith(watch_episode['href']):
                # We match!
                srch = re.search(
                    "changer_episode\((.*), '(.*)', '(.*)', '(.*)', '.*'\);",
                    watch_episode['onclick'])
                if srch:
                    show_id, ep_season, ep_episode, version, = srch.groups()
                    new_url = self.BASE_URL + \
                              '/fichiers/includes/inc_afficher_serie' \
                              '/changer_episode.php?changer_episod=1&id_serie' \
                              '=%(show_id)s&saison=%(season)s&episode=' \
                              '%(episode)s&version=%(version)s' % {
                                  'show_id': show_id,
                                  'season': ep_season,
                                  'episode': ep_episode,
                                  'version': version,
                              }
                    for soup_ in self.soup_each([new_url]):
                        for iframe in soup_.select('iframe'):
                            if iframe['src'].startswith('http'):
                                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                                         link_url=iframe['src'],
                                                         series_season=season,
                                                         series_episode=episode,
                                                         )
