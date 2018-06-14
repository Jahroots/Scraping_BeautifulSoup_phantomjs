# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class TunemoviesTo(SimpleScraperBase):
    BASE_URL = 'http://tunemovies.to'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def setup(self):
        raise NotImplementedError('Website no longer available.')
    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/{}.html'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Sorry, we could not find the movie that you were looking for this movie'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'Next →')
        return self.BASE_URL+next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('h2.title a'):
                self.submit_search_result(
                    link_url=results['href'],
                    link_title=results.text,
                )
                found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('ul#play_name li.active').find('a').text
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.server_line a'):
            ip_film = link['data-film']
            ip_server = link['data-server']
            ipplugins = '1'
            ip_name = link['data-name']
            data = {'ip_film': ip_film, 'ip_server': ip_server, 'ipplugins': ipplugins, 'ip_name': ip_name}
            encoded_soup = json.loads(self.post_soup('https://tunemovies.to/ip.file/swf/plugins/ipplugins.php', data=data).text)
            s = encoded_soup['s']

            movie_soup = json.loads(self.get_soup('https://tunemovies.to/ip.file/swf/ipplayer/ipplayer.php?u={}&w=100%25&h=420&s=2&n=0'.format(s)).text)
            movie_link = movie_soup['data']
            if movie_link:
                for link in movie_link:
                    if len(link) == 1:
                        continue

                    url = link['files']
                    self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=url,
                            link_text=title,
                        )

