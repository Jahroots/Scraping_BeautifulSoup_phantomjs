# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class AltadefinizioneClub(SimpleScraperBase):
    BASE_URL = 'https://altadefinizione.bid'
    OTHER_URLS = ['http://altadefinizione.bid']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ita'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Nessun post da mostrare.'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text=u'Pagina successiva »')
        self.log.debug('---------------')
        return next['href'] if next else None

    def _parse_search_result_page(self, soup):
        find = 0
        for results in soup.select('ul.posts a'):
            if '/4k/' in results['href']:
                continue
            result = results['href']
            title = results.text.strip()
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            find=1
        if not find:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        download_links= soup.select('div#embeds iframe')
        for download_link in download_links:
            movie_link = download_link['src']
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link,
                link_text=title,
            )
        movie_links = soup.select('div.pad a')
        for movie_link in movie_links:
            if '#' in movie_link['href']:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=movie_link['href'],
                link_text=title,
            )
