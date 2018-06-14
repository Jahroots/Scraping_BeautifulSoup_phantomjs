# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


# the room for improvement
# see https://github.com/denniskis/kodiplugins/blob/master/plugin.video.kinobar.net/default.py

class KinoBarNet(SimpleScraperBase):
    BASE_URL = 'http://kinobar.net'
    OTHER_URLS = ['http://tfilm.space', 'http://tfilm.tv', 'http://tfilm.me']
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True

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

    def get(self, url, **kwargs):
        return super(KinoBarNet, self).get(url, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?search=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'По вашему запросу ничего не найдено'

    def _fetch_next_button(self, soup):
        link = soup.find('span', text='»')
        if link:
            self.log.debug('----------------')
            return link.parent['href']

    def _parse_search_result_page(self, soup):
        for title in soup.select('div.mat-title'):
            link = title.find('a')
            image = None
            next_sibling = title.find_next_sibling()

            if next_sibling and \
                            'class' in next_sibling.attrs and \
                            next_sibling['class'] == ['mat-images']:
                image = next_sibling.find('img')['src']

            self.submit_search_result(
                link_url=self.BASE_URL + '/' + link['href'].strip(),
                link_title=link.text.strip(),
                image=image
            )

    def _extract_movie_from_url(self, url):
        if not url:
            return

        try:
            title = self.get_soup(url).title
            if title:
                title = title.text.strip()

            if url.find('sv1.kinobar.net') >= 0:
                # Seems to be a local server - open that link and look
                # for the iframe in there
                page = self.get(url)
                # And rip out file : '...'
                match = re.search("file : '(.*?)',", page.content)
                if match:
                    self.submit_parse_result(index_page_title=title,
                                             link_url=match.group(1).strip()
                                             )
            else:
                self.submit_parse_result(index_page_title=title,
                                         link_url=url.strip()
                                         )
        except Exception as e:
            self.log.warning(e)
            return

    def _parse_parse_page(self, soup):
        for option in soup.select('select option'):
            link = option.get('value').strip()
            if link.startswith("http://vkontakte.ru/video_ext.php?"):
                try:
                    page = self.get(link, headers={'Referer': self.BASE_URL})
                    self.submit_parse_result(
                        index_page_title= self.util.get_page_title(soup),
                        link_url=page.url.strip()
                    )
                except:
                    self.submit_parse_result("Could not fetch external embed page")
            elif link.startswith("http"):
                self.submit_parse_result(
                    index_page_title= self.util.get_page_title(soup),
                    link_url=link.strip()
                )

        for iframe in soup.select('iframe'):
            self._extract_movie_from_url(iframe['src'])

        for obj in soup.select('object'):
            self._extract_movie_from_url(obj['data'])
