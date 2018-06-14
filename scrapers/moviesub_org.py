# coding=utf-8
import json


from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class MoviesubOrg(SimpleScraperBase):
    BASE_URL = 'https://moviesub.is'
    OTHER_URLS = 'http://moviesub.org'

    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    LONG_SEARCH_RESULT_KEYWORD = 'man'
    USER_AGENT_MOBILE = False

    def setup(self):
        super(self.__class__, self).setup()
        self._request_connect_timeout = 300
        self._request_response_timeout = 300


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/{}.html'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', title=u'Next')
        return self.BASE_URL+ next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):

        found = 0
        for results in soup.select('ul.cfv a[class="th tooltip"]'):
            title = results.text
            self.submit_search_result(
                link_url=results['href'],
                link_title=title,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        title = soup.select_one('h2')
        if title and title.text:
            title = title.text

        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('#servers-list a'):
            ip_film = link['data-film']
            ip_server = link['data-server']
            ipplugins = '1'
            ip_name = link['data-name']
            data = {'ip_film': ip_film, 'ip_server': ip_server, 'ipplugins': ipplugins, 'ip_name': ip_name}
            encoded_soup = json.loads(
                self.post_soup('https://moviesub.is/ip.file/swf/plugins/ipplugins.php', data=data).text)
            s = encoded_soup['s']
            movie_soup = json.loads(
                self.get_soup('https://moviesub.is/ip.file/swf/ipplayer/ipplayer.php?u={}&w=100%25&h=450&s=2&n=0'.format(s)).text)

            movie_link = movie_soup['data']
            if movie_link and type(movie_link) is list:
                for link in movie_link:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link['files'],
                        link_text=title,
                    )
            elif movie_link:
                if 'http' not in movie_link:
                    movie_link = 'http:' + movie_link
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_text=title,
                )