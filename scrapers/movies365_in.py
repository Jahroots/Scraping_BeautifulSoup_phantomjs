# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class Movies365In(SimpleScraperBase):
    BASE_URL = 'http://movies365.co.in'
    OTHERS_URLS = ['http://dlmovies365.com', 'http://movies365.lol', 'http://movies365.ws', 'https://movies365.cc', 'http://movies365.ws', 'https://movies365.org', 'http://movies365.org',
                   'https://movies365.me', 'http://movies365.me', 'http://movies365.cc']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'No matches'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):

        for results in soup.select('h2[class="entry-title post-title"] a'):
            if not results:
               return self.submit_search_no_results()

            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1.entry-title').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.select('h4[style="text-align: center;"] a[target="_blank"]')
        for result in results:

            href = result['href']
            if href.find('http:') == -1 and href.find('https:') == -1:
                href = 'http:/' + href

            if 'docs' in href:
                continue

            self.log.debug(href)
            self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url= href,
                    link_text=title,
                )
