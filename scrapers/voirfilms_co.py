# -*- coding: utf-8 -*-
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, ScraperParseException, CloudFlareDDOSProtectionMixin, CachedCookieSessionsMixin
from sandcrawler.scraper.caching import cacheable


class VoirFilms(SimpleScraperBase):
    BASE_URL = 'http://www.voirfilms.ws'
    OTHER_URLS = ['http://www.voirfilms.info', 'http://www.voirfilms.biz', 'http://www.voirfilms.co']
    item = ''
    REQUIRES_WEBDRIVER = ('parse',)
    WEBDRIVER_TYPE = 'phantomjs'


    def _get_cloudflare_action_url(self):
        return self._fetch_search_url(self.item)

    def _fetch_search_url(self, search_term):
        return self.BASE_URL + '/recherche?story={}'.format(search_term)

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'afr'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def search(self, search_term, media_type, **extra):
        self.item = search_term

        search_soup = self.get_soup(self._fetch_search_url(search_term))

        results = search_soup.select('div.left-content div.mos_titre a')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        self._parse_search_results(search_soup)

    def _parse_search_result_page(self, soup):

        for link in soup.select('div.left-content div.mos_titre a'):
            url = self.util.canonicalise(self.BASE_URL,link.href)
            if 'serie' in url:
                series_soup = self.get_soup(url)
                for season_link in series_soup.select('div.unepetitesaisons a'):
                    season_soup = self.get_soup(season_link.href)
                    for episode_link in season_soup.select('div.description li.description132 a'):
                        found = True
                        self.submit_search_result(
                            link_url=episode_link.href,
                            link_title=episode_link.text.strip(),
                        )
            else:
                title = link.find('div')
                if title:
                    title = title.text
                else:
                    attrib = link.attrs
                    if 'title' in attrib:
                        title = attrib['title']
                    else:
                        title = ''

                self.submit_search_result(
                    link_url= url,
                    link_title=title.strip(),
                )

        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(self.BASE_URL + '/recherche', data = { 'story' : self.item,
                                                                       'page' : next_button.select_one('input[name="page"]')['value']
                                                                    }
                           )
            self._parse_search_result_page(soup)



    def _fetch_no_results_text(self):
        return u'La recherche n\'a retourné aucun résultat.'

    def _fetch_next_button(self, soup):
        next_link = soup.find('button', text='suiv »')
        if next_link:
            return next_link.parent
        return

    @cacheable()
    def _follow_redirect(self, url):
        return self.get_redirect_location(url)

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)

        for link in soup.select('a[data-src]'):
            url = link['data-src']
            self.webdriver().get(url)
            url = self.webdriver().current_url

            #url = self.get_soup(url)#self._follow_redirect(url)

            if url:
                self.submit_parse_result(
                        link_url=url,
                        link_title=link.text,
                        index_page_title=index_page_title
                )


        