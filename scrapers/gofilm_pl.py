# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class GofilmPl(SimpleScraperBase):
    BASE_URL = 'http://sevelt.pl/gofilm'
    OTHER_URLS = ['http://www.gofilm.pl']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'pol'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    def setup(self):
        raise NotImplementedError('the website returns 404 error.')

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/szukaj'

    def _fetch_no_results_text(self):
        return u'Nie ma żadnych wyników wyszukiwania!'

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self._fetch_search_url(search_term,media_type), data = {'search': search_term})
        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):
        results = soup.select('a')

        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            link = result.href
            if '/film/' in link:
                self.submit_search_result(
                    link_url=link,
                    link_title=result.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )
            else:
                ep_links_soup = self.get_soup(link)
                ep_links = ep_links_soup.select('li.episode a')
                for ep_link in ep_links:

                    self.submit_search_result(
                        link_url=ep_link.href,
                        link_title=ep_link.text,
                        image=self.util.find_image_src_or_none(ep_link, 'img'),
                    )


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h2').text
        link = soup.select_one('a[class="btn btn-primary"]')
        if link:
            link=link.href
        for link in soup.select('div.tab-pane iframe'):
            if '.dwn.' not in link['src']:
                link= self.get_soup(link['src']).select_one('iframe')['src']
                if 'http' not in link:
                    link = 'http:'+link
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_title=title,
                    )
            else:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=link['src'],
                    link_title=title,
                )

