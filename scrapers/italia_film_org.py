#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase, CloudFlareDDOSProtectionMixin
from sandcrawler.scraper import SimpleScraperBase


class ItaliaFilmOrg(CloudFlareDDOSProtectionMixin, SimpleScraperBase):

    BASE_URL = 'http://www.italia-film.online'
    OTHER_URLS = ['http://www.italia-film.gratis', 'http://www.italia-film.me', ]

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "ita"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self._request_size_limit = (1024 * 1024 * 10) # Bytes
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'


    def _fetch_no_results_text(self):
        return 'Non trovato'

    def _fetch_next_button(self, soup):
        link = soup.find('a', 'next', text=u'→')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('article.post'):
            link = result.select('h3.entry-title a')[0]
            img = result.select('div.entry-summary img')[0]
            image = img['src']
            if image.startswith('//'):
                image = 'http:' + image

            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=image
            )

    def _extract_season_episode(self, string):
        """
        Mtches  9×22
        """
        series, episode = (None, None)
        # The series page url contains "<name>_sX_eY"
        m = re.search(u'(\d+)\xd7(\d+)', string, re.UNICODE)
        if m:
            series, episode = m.groups()
            series = int(series)
            episode = int(episode)

        return series, episode


    def _parse_parse_page(self, soup):
        content = soup.find('div', 'entry-content')
        for iframe in content.select('iframe'):
            if 'youtube' in iframe['src'] or 'imdb' in iframe['src']:
                continue
            movie_link = iframe['src']
            if 'http' not in movie_link:
                movie_link = 'http:' + movie_link
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=movie_link,
                                     )

        season, episode = None, None
        for link in content.select('a'):
            if 'href' not in link.attrs:
                continue
            if link['href'].startswith(self.BASE_URL) or 'youtube' in link['href'] or 'imdb' in link['href']:
                continue
            # Generally layed out with the first link having the
            # season and epsiode; if it's defined, keep it around for
            # subsequent link.s
            this_season, this_episode = self._extract_season_episode(
                link.text)
            if this_season and this_episode:
                season = this_season
                episode = this_episode
            movie_link = link['href']
            if 'http' not in movie_link:
                movie_link = 'http:'+movie_link
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=movie_link,
                                     link_title=link.text,
                                     series_season=season,
                                     series_episode=episode,
                                     )



