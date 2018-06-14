# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ColdfilmRu(SimpleScraperBase):
    BASE_URL = 'http://coldfilm.info'
    OTHER_URLS = ['http://coldfilm.ru']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP , ]
    LANGUAGE = 'rus'
    LONG_SEARCH_RESULT_KEYWORD = u'игра престолов'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV ]
    URL_TYPES = [ ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING ]
    LONG_SEARCH_RESULT_KEYWORD = '2017'
    PAGE = 1
    SEARCH_TERM = ''
    TRELLO_ID = 'KJudZf39'


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/?q={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'По запросу ничего не найдено'

    def _fetch_next_button(self, soup):
        self.PAGE += 1
        link = self.BASE_URL + '/search/?q={};t=0;p={};md='.format(self.SEARCH_TERM, self.PAGE)
        self.log.debug('------------------------')
        return link if link else None


    def search(self, search_term, media_type, **extra):
        self.PAGE = 1
        self.SEARCH_TERM = search_term
        super(self.__class__, self).search(search_term, media_type, **extra)

    def _parse_search_result_page(self, soup):
        results = soup.select('a[class="sres-wrap clearfix"]')
        for results in results:
            #forums = results.find('div', 'eDetails').text
            #if u'Новинки кино' in forums or u'Новости сайта' in forums or u'Каталог сериалов' in forums or u'Каталог фильмов' in forums:
             #   result = results.find('div', 'eTitle').find('a')['href']
             #   title = results.find('div', 'eTitle').find('a').text.strip()
                self.submit_search_result(
                    link_url=results.href,
                    link_title=results.text
                )

    def _parse_parse_page(self, soup):
        #self.log.debug(soup)
        title = soup.select_one('div.eTitle')
        if not title:
            title = soup.select_one('h1')

        title = title.text.strip()
        for link in soup.select('iframe[allowfullscreen]'):
            movie_link = link['src']

            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=movie_link,
                link_text=title,
            )
        for torrent_links in soup.select('a'):
            torrent_link = ''
            try:
                torrent_link = torrent_links['href']
            except KeyError:
                pass
            if '.torrent' in torrent_link:
               movie_link = torrent_links['href']
               self.submit_parse_result(
                   index_page_title=self.util.get_page_title(soup),
                   link_url=movie_link,
                   link_text=title,
                   )