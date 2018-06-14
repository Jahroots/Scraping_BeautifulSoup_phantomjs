# coding=utf-8

import json
import re

import requests

from sandcrawler.scraper import ScraperBase


class FilmPalastTo(ScraperBase):
    BASE_URL = 'http://filmpalast.to'
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'deu'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]

    def search(self, search_term, media_type, **extra):
        self._parse_search_results(
            self.post_soup(
                self.BASE_URL + '/search/title/' + search_term,
                data={
                    'headerSearchText': search_term,
                    't1': 'tags',
                }
            )
        )

    def _parse_search_results(self, soup):
        if unicode(soup).find(u'Suchergebnisse: 0') >= 0:
            return self.submit_search_no_results()
        for result in soup.select('article.liste'):
            link = result.select('h2.rb a')[0]
            (season, episode) = self.util.extract_season_episode(link.text)
            image = result.select('img')[-1]['src']
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                series_season=season,
                series_episode=episode,
                image=self.BASE_URL + image
            )

        next_button = soup.find('div', {'id': 'paging'}) \
            .find('a', text=re.compile('\+'))
        if next_button and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button['href'])
            )

    def parse(self, parse_url, **extra):

        for soup in self.soup_each([parse_url, ]):
            title = soup.select_one('.bgDark.rb').text.strip()

            for result in soup.select('.streamEpisodeTitle a'):
                id_ = result.attrs['data-id']
                jsn = json.loads(
                    requests.post(self.BASE_URL + '/stream/{id_}/1'.format(id_=id_),
                                  data={'streamID': id_},
                                  headers={
                                      'X-Requested-With': 'XMLHttpRequest',
                                  }).content)
                # print(jsn)
                if jsn.get('error') == '1':
                    continue
                parse_url = jsn['url']
                (season, episode) = self.util.extract_season_episode(parse_url)
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=parse_url,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode,
                                         )
