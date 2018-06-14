# coding=utf-8

import re

from sandcrawler.scraper import FlashVarsMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class MyHitOrg(SimpleScraperBase, FlashVarsMixin):
    BASE_URL = 'https://my-hit.org'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?q=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'К сожалению, по данному запросу ничего не найдено.'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'Вперед »')
        if link:
            return self.BASE_URL + link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.film-list > div.row'):
            image = result.find('img', 'img-rounded')['src']
            submitted = set()
            for link in result.findAll('a',
                                       attrs={'href': re.compile('/serial'),
                                              'title': True, }):
                if link['href'] not in submitted:
                    self.submit_search_result(
                        link_url=self.BASE_URL + link['href'],
                        link_title=link['title'],
                        image=self.BASE_URL + image,
                        asset_type=ScraperBase.MEDIA_TYPE_TV
                    )
                    submitted.add(link['href'])
            for link in result.findAll('a',
                                       attrs={'href': re.compile('/film'),
                                              'title': True}):
                if link['href'] not in submitted:
                    self.submit_search_result(
                        link_url=self.BASE_URL + link['href'],
                        link_title=link['title'],
                        image=self.BASE_URL + image,
                        asset_type=ScraperBase.MEDIA_TYPE_FILM
                    )
                    submitted.add(link['href'])


    def parse(self, parse_url, **extra):
        contents = self.get(parse_url).content
        match = re.search('flashvars = ({.*?})', contents)
        if match:
            # Dig out the flash vars js
            # flashvars = {m:'video', st:'/player/style/flash/4-5-6/0/style.txt?v=22', 'pl':'/serial/9/playlist.txt', 'poster':'/storage/kadr/29586/27_1920x1080x250.jpg', nocache:1}
            self._parse_flashvars_from_javascript_hash(match.group(1))
