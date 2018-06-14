# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
from sandcrawler.scraper.caching import cacheable
import re
import base64
import json

class VungtvCom(SimpleScraperBase):
    BASE_URL = 'http://vung.tv'
    OTHER_URLS = ['http://vungtv.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'vie'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    USER_AGENT_MOBILE = False

    def get(self, url, **kwargs):
        """
        Site has a location check - all it does is set a cookie, so do so manually.
        """
        self._http_session.cookies.set(
            '__ct',
            'VNM',
            domain='vungtv.com')
        return super(VungtvCom, self).get(url, **kwargs)


    def _fetch_search_url(self, search_term, media_type):
        return u'{}/tim-kiem/?q={}'.format(self.BASE_URL, self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'KHÔNG TÌM THẤY PHIM PHÙ HỢP VỚI TỪ KHOÁ'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('ul.page-category li.pag-next a')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.group-film-small a.film-small'):
            self.submit_search_result(
                link_url=result.href,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )


    @cacheable()
    def _find_links(self, url):

        links = []
        soup = self.get_soup(url)
        iframe = soup.select_one('div.player-film iframe')
        iframe_source = self.get(iframe['src']).content
        for ref in ('sources', 'hash'):

            srch = re.search(
                "{}: '(.*?)'".format(ref),
                iframe_source,
            )
            if srch:
                for source in json.loads(base64.decodestring(srch.group(1))):
                    links.append(
                        source['file']
                    )
        return links

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)

        # Several pages have a 'coming soon' link, but no actual video available.
        play_film = soup.select_one('a.play-film')
        if play_film:
            film_soup = self.get_soup(play_film.href)
            episode_links = \
                [play_film.href, ] + \
                [l.href for l in film_soup.select('div.episode-main ul li a')]
            for episode in episode_links:
                for link in self._find_links(episode):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                    )
