# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import re


class PapystreamingOrg(SimpleScraperBase):
    BASE_URL = 'https://papystreaming-2018.com'
    OTHERS_URLS = ['https://papystreaming-hd.com', 'https://papy-streaming.org', 'https://papystreaming.org', 'http://papystreaming.org',
                   'https://papystreaming.org', 'https://papystreaming-hd.org']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[403], verify=False, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'0 Résultat trouvé'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for results in soup.select('h3.name a'):
            if not results:
               return self.submit_search_no_results()
            result = results['href']
            title = results.text
            self.submit_search_result(
                    link_url=result,
                    link_title=title,
                )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        links = json.loads(soup.find('div', id='online').find('script').text.split('repron_links=')[-1])
        for link in links:
            movie_link = link['link'].replace( '////', '//')

            if 'http' not in movie_link:
                movie_link = 'http:' + movie_link

            if 'player.papystreaming' in movie_link:
                if 'http' not in movie_link:
                    movie_link = 'http:'+ movie_link

                if 'http' and 'https' in movie_link:
                    movie_link = 'https:' + movie_link.split('https:')[1]


                papy_soup = self.get_soup(movie_link)
                papy_iframe = papy_soup.find('iframe')['src']


                papy_url = self.get_redirect_location(papy_iframe)


                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=papy_url,
                    link_text=title,
                )
            else:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_text=title,
                )
