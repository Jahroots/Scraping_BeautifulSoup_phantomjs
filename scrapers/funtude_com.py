# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FuntudeCom(SimpleScraperBase):
    BASE_URL = 'http://www.funtude.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'chi'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return u'總共0 個結果'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?key={}'.format(self.util.quote(search_term))


    def _fetch_next_button(self, soup):
        link = ''
        try:
            link = soup.find('a', text=u'下一頁')
        except AttributeError:
            pass
        self.log.debug('------------------------')
        return self.BASE_URL+'/search.php'+link['href'] if link else None


    def _parse_search_result_page(self, soup):
        any_results = False
        for results in soup.select('div#search-list div.showTxt a'):
            result = results['href']
            link_soup = self.get_soup(self.BASE_URL+result)
            title = link_soup.select_one('div#title').text.split(':')[-1].strip()
            for ep_link in link_soup.select('div#tab1 a'):
                if 'baidu.com' in ep_link['href'] or 'google.com' in ep_link['href']:
                    continue
                self.submit_search_result(
                    link_url=ep_link['href'],
                    link_title=title
                )
                any_results = True
        if not any_results:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        title = soup.select_one('div#title').text.strip()
        link = soup.select_one('div#videoOutLink a')
        if link:
            link=link['href']
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=link,
                                     link_title=title,
                                 )