# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FilmesserieshdCom(SimpleScraperBase):
    BASE_URL = 'http://filmesserieshd.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'por'

    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]


    def get(self, url, **kwargs):
        return self._do_request_action('get', url, allowed_errors_codes=[405], **kwargs)

    def _request_action(self, action, url, **kwargs):
        method = getattr(self.http_session(), action)
        timeout = (self._request_connect_timeout, self._request_response_timeout)
        r = method(url, timeout=timeout, stream=True, **kwargs)
        return r

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Conteúdo não disponível'

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'PrĂłxima ›')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for results in soup.select('div#resultados span.titulo a'):
            result = results['href']
            title = results.text
            self.submit_search_result(
                    link_url=result,
                    link_title=title,
                )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        iframe_link = soup.select_one('div#div1 iframe')['src']
        series_soup = self.get_soup(iframe_link)
        movie_links = series_soup.select('li.abrirPlay')
        for movie_link in movie_links:
            secured_redirect_url = self.get_redirect_location(movie_link['data-play'])
            if secured_redirect_url:
                redirect_url = self.get(secured_redirect_url).url
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=redirect_url,
                    link_text=title,
                )
        links = series_soup.select('a.btn')
        for link in links:
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=link.href,
                link_text=title,
            )
