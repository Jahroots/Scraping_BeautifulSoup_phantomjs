# coding=utf-8
import base64
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import VideoCaptureMixin


class MegaShareAt(ScraperBase, VideoCaptureMixin):
    BASE_URL = 'http://www.primewire.ag'
    OTHER_URLS = ['http://megashare.at']
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('Deprecated. Duplicate of primewire_ag.py.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

        self.requires_webdriver = ('parse',)
        self.webdriver_type = 'phantomjs'

    def _do_search(self, search_term, page=1):
        return self.post_soup(
            self.BASE_URL + '/index.php',
            data={'obj': 'Search,' + search_term,
                  'page': page,
                  'view': 1,
                  }
        )

    def search(self, search_term, media_type, **extra):
        first_page = self._do_search(search_term)

        if unicode(first_page).find('No movies found match') >= 0:
            return self.submit_search_no_results()

        self._parse_search_result_page(first_page)

        # Iterate through the pages until we don't have a next button link.
        page = 1
        next_button_link = self._fetch_next_button(first_page)
        while next_button_link and self.can_fetch_next():
            page += 1
            soup = self._do_search(
                search_term,
                page
            )
            self._parse_search_result_page(soup)
            next_button_link = self._fetch_next_button(soup)

    def _fetch_next_button(self, soup):
        link = soup.find('a', {'title': 'Next Pages'})
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        # A bit meh, but there are no useful ids or classes
        # Grab the top level one and dig through tables
        for td in soup.select('table table table td'):
            link = td.find('a', 'FilmName')
            if not link:
                continue
            filmcat_link = td.find('a', 'FilmCat')
            season, episode, image, asset_type = \
                None, None, None, ScraperBase.MEDIA_TYPE_FILM
            if filmcat_link and filmcat_link.text.find('Series') >= 0:
                season, episode = self.util.extract_season_episode(link.text)
                asset_type = ScraperBase.MEDIA_TYPE_FILM
            img = td.find('img')
            if img:
                image = img['src']

            self.submit_search_result(
                link_url=self.BASE_URL + '/' + link['href'],
                link_title=link.text,
                series_season=season,
                series_episode=episode,
                asset_type=asset_type,
                image=image,
            )

    def _video_player_classes(self):
        return ()

    def _video_player_ids(self):
        return ('flashplayer', 'player1')

    def _packet_matches_playlist(self, packet):
        return False

    def parse(self, parse_url, **extra):

        soup = self.get_soup(parse_url)

        self._parse_parse_page(parse_url)
        for link in soup.select('ul.alternative li a'):
            self._parse_parse_page(self.BASE_URL + '/' + link['href'])

    def _parse_parse_page(self, parse_url):


        soups = []
        html = self.get(parse_url).text
        soups.append(self.make_soup(html))

        index_page_title = self.util.get_page_title(soups[0])

        try:
            the = self.util.unquote(base64.decodestring(
                html.split("document.write(doit('")[1].split("'))</script>")[0]))
        except IndexError:
            pass
        else:
            soups.append(self.make_soup(the))


        found_iframe = False

        for soup in soups:
            for fr in soup.select('iframe'):
                if self.BASE_URL not in fr['src']:
                    if 'share_button' in fr['src'] or 'plugins/like' in fr['src']:
                        continue
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=fr['src']
                        )
                    found_iframe = True

        # Don't bother with video capture if we already have the video.
        if found_iframe:
            return

        for url in self._capture_video_urls(parse_url):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url
            )


if __name__ == '__main__':
    import base64, urllib

    # print (urllib.unquote(
    #     base64.decodestring(
    #         'QTdqdjBEd2I4aXRzSjZtNksxOHJiOXJ6T3BaS2xzZ3cxTXlqVlRodi95VWJMcy9ZRkRTUzlkczN1aGp0LzltUW5XczFKc1hIV1NMUGZSWkVrQit1UXRtYmRXMWhLWEpHMmFGWlZNUkc1bnF3UlY5VEtkQ04yUUJxcmtqakhtYW8=')) \
    #     )
    # print
    #
    # print (urllib.unquote(
    #     base64.decodestring(
    #         'JTNDc2NyaXB0JTIwdHlwZSUzRCUyMnRleHQlMkZqYXZhc2NyaXB0JTIyJTIwc3JjJTNEJTIyaHR0cCUzQSUyRiUyRm1lZ2FzaGFyZS5zYyUyRm1vZHVsZXMlMkZwaWMlMkZwbHVnaW5zJTJGZ2twbHVnaW5zcGhwLmpzJTIyJTNFJTNDJTJGc2NyaXB0JTNFJTBBJTNDZGl2JTIwaWQlM0QlMjJwbGF5ZXIxJTIyJTIwc3R5bGUlM0QlMjJ3aWR0aCUzQTY4OHB4JTNCaGVpZ2h0JTNBNDM4cHglM0JiYWNrZ3JvdW5kLWNvbG9yJTNBJTIzOTk5JTIyJTNFJTNDJTJGZGl2JTNFJTBBJTNDc2NyaXB0JTIwdHlwZSUzRCUyMnRleHQlMkZqYXZhc2NyaXB0JTIyJTNFJTBBZ2twbHVnaW5zcGhwJTI4JTIycGxheWVyMSUyMiUyQyU3QmxpbmslM0ElMjJRVGRxZGpCRWQySTRhWFJ6U2padE5rc3hPSEppT1hKNlQzQmFTMnh6WjNjeFRYbHFWbFJvZGk5NVZXSk1jeTlaUmtSVFV6bGtjek4xYUdwMEx6bHRVVzVYY3pGS2MxaElWMU5NVUdaU1drVnJRaXQxVVhSdFltUlhNV2hMV0VwSE1tRkdXbFpOVWtjMWJuRjNVbFk1VkV0a1EwNHlVVUp4Y210cWFraHRZVzglM0QlMjIlN0QlMjklM0IlMEElM0MlMkZzY3JpcHQlM0U=')) \
    #     )
    # print
    #
    # print (urllib.unquote(
    #     base64.decodestring(
    #         'JTNDaWZyYW1lJTIwc3JjJTNEJTIyaHR0cCUzQSUyRiUyRnZpZC5hZyUyRmVtYmVkLW9rY3BibmRiOTkxZy5odG1sJTIyJTIwd2lkdGglM0QlMjI2ODglMjIlMjBoZWlnaHQlM0QlMjI0MzglMjIlMjBmcmFtZWJvcmRlciUzRCUyMjAlMjIlMjBzY3JvbGxpbmclM0QlMjJubyUyMiUyMGFsbG93ZnVsbHNjcmVlbiUzRCUyMnRydWUlMjIlMjB3ZWJraXRhbGxvd2Z1bGxzY3JlZW4lM0QlMjJ0cnVlJTIyJTIwbW96YWxsb3dmdWxsc2NyZWVuJTNEJTIydHJ1ZSUyMiUzRSUzQyUyRmlmcmFtZSUzRQ=='))
    # )
    # print
    #
    # print (urllib.unquote(
    #     base64.decodestring(
    #         'JTNDc2NyaXB0JTIwdHlwZSUzRCUyMnRleHQlMkZqYXZhc2NyaXB0JTIyJTIwc3JjJTNEJTIyaHR0cCUzQSUyRiUyRm1lZ2FzaGFyZS5zYyUyRm1vZHVsZXMlMkZwaWMlMkZwbHVnaW5zJTJGZ2twbHVnaW5zcGhwLmpzJTIyJTNFJTNDJTJGc2NyaXB0JTNFJTBBJTNDZGl2JTIwaWQlM0QlMjJwbGF5ZXIxJTIyJTIwc3R5bGUlM0QlMjJ3aWR0aCUzQTY4OHB4JTNCaGVpZ2h0JTNBNDM4cHglM0JiYWNrZ3JvdW5kLWNvbG9yJTNBJTIzOTk5JTIyJTNFJTNDJTJGZGl2JTNFJTBBJTNDc2NyaXB0JTIwdHlwZSUzRCUyMnRleHQlMkZqYXZhc2NyaXB0JTIyJTNFJTBBZ2twbHVnaW5zcGhwJTI4JTIycGxheWVyMSUyMiUyQyU3QmxpbmslM0ElMjJRVGRxZGpCRWQySTRhWFJ6U2padE5rc3hPSEppT1hKNlQzQmFTMnh6WjNjeFRYbHFWbFJvZGk5NVZXSk1jeTlaUmtSVFV6bGtjek4xYUdwMEx6bHRVVzVYY3pGS2MxaElWMU5NVUdaU1drVnJRaXQxVVhSdFltUlhNV2hMV0VwSE1tRkdXbFpOVWtjMWJuRjNVbFk1VkV0a1EwNHlVVUp4Y210cWFraHRZVzglM0QlMjIlN0QlMjklM0IlMEElM0MlMkZzY3JpcHQlM0U='))
    #        .split('{link:"')[1].split('"});')[0])
    # print
    #
    # print base64.decodestring(base64.decodestring(urllib.unquote(
    #     base64.decodestring(
    #         'JTNDc2NyaXB0JTIwdHlwZSUzRCUyMnRleHQlMkZqYXZhc2NyaXB0JTIyJTIwc3JjJTNEJTIyaHR0cCUzQSUyRiUyRm1lZ2FzaGFyZS5zYyUyRm1vZHVsZXMlMkZwaWMlMkZwbHVnaW5zJTJGZ2twbHVnaW5zcGhwLmpzJTIyJTNFJTNDJTJGc2NyaXB0JTNFJTBBJTNDZGl2JTIwaWQlM0QlMjJwbGF5ZXIxJTIyJTIwc3R5bGUlM0QlMjJ3aWR0aCUzQTY4OHB4JTNCaGVpZ2h0JTNBNDM4cHglM0JiYWNrZ3JvdW5kLWNvbG9yJTNBJTIzOTk5JTIyJTNFJTNDJTJGZGl2JTNFJTBBJTNDc2NyaXB0JTIwdHlwZSUzRCUyMnRleHQlMkZqYXZhc2NyaXB0JTIyJTNFJTBBZ2twbHVnaW5zcGhwJTI4JTIycGxheWVyMSUyMiUyQyU3QmxpbmslM0ElMjJRVGRxZGpCRWQySTRhWFJ6U2padE5rc3hPSEppT1hKNlQzQmFTMnh6WjNjeFRYbHFWbFJvZGk5NVZXSk1jeTlaUmtSVFV6bGtjek4xYUdwMEx6bHRVVzVYY3pGS2MxaElWMU5NVUdaU1drVnJRaXQxVVhSdFltUlhNV2hMV0VwSE1tRkdXbFpOVWtjMWJuRjNVbFk1VkV0a1EwNHlVVUp4Y210cWFraHRZVzglM0QlMjIlN0QlMjklM0IlMEElM0MlMkZzY3JpcHQlM0U=')) \
    #                                               .split('{link:"')[1].split('"});')[0]))
