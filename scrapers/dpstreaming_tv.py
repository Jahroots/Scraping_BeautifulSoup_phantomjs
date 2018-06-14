# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class DpstreamingTv(SimpleScraperBase):
    BASE_URL = 'http://dpstreaming.cc'
    OTHERS_URLS = ['http://DpStreaming.cc/', 'http://dpstreaming.ws', 'http://dpstreaming.me']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    # SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Désolé, aucun poste correspondant à vos critères'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for results in soup.select('div.title h2 a'):
            if not results:
               return self.submit_search_no_results()
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result.lower(),
                link_title=title
            )

    def _parse_parse_page(self, soup):
        title = soup.select_one('div.title h2').text.strip()
        index_page_title = self.util.get_page_title(soup)
        results = soup.find('div', 'entry').find_all('p', attrs={'align':'center'})
        for result in results:
            for movie_link in result.find_all('a'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link['href'],
                    link_text=title,
                )