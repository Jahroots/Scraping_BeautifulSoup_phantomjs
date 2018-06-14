# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase, ScraperParseException


class MegaFilmesOnlineNet(SimpleScraperBase):
    BASE_URL = 'https://megafilmesonline.net'
    OTHER_URLS = ['http://megafilmesonline.net']
    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "por"
        raise NotImplementedError('The website is out of reach')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'Desculpe, a página que você procura não pode ser encontrada.'

    def _fetch_next_button(self, soup):
        link = soup.select_one('a.nextpostslink')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div#lista-posts div.box-video div.content a.thumb'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title'],
                image=self.util.find_image_src_or_none(soup, 'img')
            )



    def _parse_parse_page(self, soup):
        MARKER = 'http://www.megafilmesonline.net/ad/?video='
        PROTECTOR_MARKER = '/protetor/?video='
        index_page_title = self.util.get_page_title(soup)

        for iframe in soup.select('div.servers iframe'):
            # Often uses a local landing page eg:
            # http://www.megafilmesonline.net/ad/?video=http://www.ok.ru/videoembed/27087735410
            # Check to make sure it matches, then submit
            src = iframe.get('src', iframe.get('data-src', None))
            if not src:
                raise ScraperParseException('Could not find iframe src: %s' % iframe)

            src = src.replace('/protetor/?video=', '').replace('/ads/?video=', '')
            if src.startswith(MARKER):
                url = src[len(MARKER):]
                url = url[len(PROTECTOR_MARKER):] if url.startswith(PROTECTOR_MARKER) else url
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url,
                )
            else:
                # Otherwise, just submit that link.
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=src,
                )
