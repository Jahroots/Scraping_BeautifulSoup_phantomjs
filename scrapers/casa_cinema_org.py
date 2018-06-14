# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class CasaCinemaOrg(SimpleScraperBase):
    BASE_URL = 'https://www.casacinema.video'
    OTHER_URLS = ['http://www.casacinema.video','http://www.casacinema.click', ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    SINGLE_RESULTS_PAGE = True


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Nessun post da mostrare'

    def _fetch_next_button(self, soup):
        # Pagination is bung on this site - next page returns *all* videos.
        return None
        next_link = soup.find('a', text=u'Pagina successiva »')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('ul.posts li'):
            title = results.a.text
            self.submit_search_result(
                link_url=results.a['href'],
                link_title=title,
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text
        index_page_title = self.util.get_page_title(soup)
        for link in soup.select('div.embed iframe')+soup.select('div#links a'):
            try:
                movie_link = link['src']
            except KeyError:
                try:
                    movie_link = link['href']
                except KeyError:
                    movie_link = link['href']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )
        for link in soup.select('div.pad a'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_text=link.text
            )