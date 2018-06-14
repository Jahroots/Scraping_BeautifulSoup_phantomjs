# -*- coding: utf-8 -*-

import re
import time

from sandcrawler.scraper import AntiCaptchaMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper import CachedCookieSessionsMixin
from sandcrawler.scraper.caching import cacheable


class SomosMoviesCom(AntiCaptchaMixin, CachedCookieSessionsMixin, SimpleScraperBase):
    BASE_URL = 'http://somosmovies.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [
        ScraperBase.MEDIA_TYPE_FILM,
        ScraperBase.MEDIA_TYPE_TV
    ]
    URL_TYPES = [
        ScraperBase.URL_TYPE_SEARCH,
        ScraperBase.URL_TYPE_LISTING,
    ]

    RECAPKEY = "6Le8uQETAAAAANpwALrazVUZjpvKeA-IWPSHJ0NS"
    TRELLO_ID = 'DgPr4v9E'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/buscar/?q=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'No se encontraron resultados para tu búsqueda'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('div.panel-body div.thumbnail a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title'],
                image=self.util.find_image_src_or_none(result, 'img')
            )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _recaptcha_on_page(self, soup):
        return soup.select_one(
            'div.recaptcha'
        )

    @cacheable()
    def get_captcha_links(self, parse_url):
        self.load_session_cookies()
        soup = self.get_soup(
            parse_url
        )
        if self._recaptcha_on_page(soup):
            key = self.get_recaptcha_token()
            verify_response = self.get(
                'http://somosmovies.com/recaptcha/verify/{}/'.format(key),
                headers={
                    'Referer': parse_url,
                    'Accept': 'application/json, text/plain, */*',
                }
            )
            if not verify_response.ok:
                raise ScraperParseException(
                    'Got invalid response for recap verify.')
            if not verify_response.json()['success']:
                raise ScraperParseException(
                    'Got not OK response for recap verify.')
            soup = self.get_soup(
                parse_url
            )
            if self._recaptcha_on_page(soup):
                raise ScraperParseException(
                    'Recapcha back on page after refresh.')
            self.save_session_cookies()

        index_page_title = self.util.get_page_title(soup)
        submitted_links = set()
        results = []
        for episodeblock in soup.find_all('div', {'id': re.compile('^S\d+E\d+$')}):
            season, episode = \
                self.util.extract_season_episode(episodeblock['id'])
            for result in episodeblock.select('a.btn'):
                if result['href'] in submitted_links:
                    continue
                submitted_links.add(result['href'])
                results.append(dict(
                    link_url=result['href'],
                    link_title=result.text.strip(),
                    index_page_title=index_page_title,
                    series_season=season,
                    series_episode=episode,
                ))


        for result in soup.select('div.tab-links tr div.collapse a.btn'):
            if result['href'] in submitted_links:
                continue
            submitted_links.add(result['href'])
            results.append(dict(
                link_url=result['href'],
                link_title=result.text.strip(),
                index_page_title=index_page_title,))
        return results

    def parse(self, parse_url, **extra):
        for result in self.get_captcha_links(parse_url):
            self.submit_parse_result(**result)
