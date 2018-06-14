# coding=utf-8

from sandcrawler.scraper import SimpleScraperBase, ScraperBase


class CineFilmesOnlineNet(SimpleScraperBase):
    BASE_URL = 'http://www.cinefilmesonline.net'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "por"
        raise NotImplementedError('http://www.cinefilmesonline.net is disabled')

        self.register_media(self.MEDIA_TYPE_FILM)
        self.register_media(self.MEDIA_TYPE_TV)

        self.register_url(self.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(self.URL_TYPE_LISTING, self.BASE_URL)

        self.proxy_region = 'bra'

    def _parse_search_result_page(self, soup):
        for lnk in soup.select('.miniatura h2 a'):
            self.submit_search_result(
                link_url=lnk.href,
                link_title=lnk['title']
            )

    def _fetch_no_results_text(self):
        return u'Nenhuma Postagem Encontrada, Tente novamente!!!'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='»')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _extract_embed(self, url, referrer):
        soup = self.get_soup(url, headers={'Referer': referrer})
        frame = soup.find('iframe')
        if frame:
            url = frame['src']
            if url.startswith("//"):
                url = "http:" + url
            return url

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)

        for frame in soup.find_all('iframe', {'allowfullscreen': ''}):
            url = frame.get('data-src') or frame.get('src')

            if 'cinefilmesonline.net' in url:
                continue

            if 'www.assistaonlinebr.net/?id=' in url:
                url = self._extract_embed(url, parse_url)

            if url != 'about:blank' and (url or '').startswith('http'):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url)
