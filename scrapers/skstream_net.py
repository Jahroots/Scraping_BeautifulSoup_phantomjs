# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class SkstreamNet(SimpleScraperBase):
    BASE_URL = 'http://www.skstream.biz'
    OTHERS_URL = ['http://www.skstream.ws', 'http://www.skstream.cc', 'http://www.skstream.co', 'http://www.skstream.org']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "fre"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/recherche?s={}'.format(search_term)

    def _fetch_no_results_text(self):
        return u'No se han encontrado resultados para tu búsqueda'

    def search(self, search_term, media_type, **extra):
        for soup in self.soup_each([self._fetch_search_url(search_term, media_type)]):
            self._parse_search_results(soup)

    def _fetch_next_button(self, soup):
        next_link = ''
        try:
            next_link = soup.find('ul', 'pagination').find_all('a')[-1]
        except IndexError:
            pass
        if not next_link:
            return self.submit_search_no_results()
        return self.BASE_URL+next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div[class*="movie_single"] a'):
            link = '{}{}'.format(self.BASE_URL, result['href'])
            if '/series/' in link:
                series_soup = self.get_soup(link)
                for eplink in series_soup.select('a.episode-block'):
                    self.submit_search_result(
                        link_url='{}{}'.format(self.BASE_URL, eplink['href']),
                        link_title=eplink['title']
                    )
            else:
                self.submit_search_result(
                    link_url=link,
                    link_title=result.text.strip(),
                )

    @cacheable()
    def _follow_link(self, url):
        return self.get(url).url

    def _parse_parse_page(self, soup):

        iframe = soup.select_one('#player iframe')
        if iframe and iframe.has_attr('src'):
            try:
                url = self._follow_link(iframe['src'])
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_title=soup.find('h3').text,
                                         link_url=url)
            except Exception as e:
                self.log.info('Video not Found: ' + str(e))


        tr = soup.select('tr[data-embedlien]')
        for t in tr:
            try:

                url = self._follow_link(t['data-embedlien'])
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_title=soup.find('h3').text,
                                         link_url=url)
            except Exception as e:
                self.log.info('Video not Found: ' + str(e))