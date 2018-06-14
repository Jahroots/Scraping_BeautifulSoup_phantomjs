# coding=utf-8


from sandcrawler.scraper import DuckDuckGo, ScraperBase, SimpleScraperBase


class ProgramasgratisfullCom(DuckDuckGo, SimpleScraperBase):
    BASE_URL = 'http://www.programasgratisfull.com'
    LONG_SEARCH_RESULT_KEYWORD = '2015'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "esp"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def get(self, url, **kwargs):
        return super(ProgramasgratisfullCom, self).get(
            url, allowed_errors_codes=[404, 403], **kwargs)

    def post(self, url, **kwargs):
        return super(self.__class__, self).post(
            url, allowed_errors_codes=[403], **kwargs)

    def parse(self, parse_url, **extra):
        redirect_soup = self.get_soup(parse_url)
        if 'peliculas-gratis/' not in redirect_soup._url and 'series/' not in redirect_soup._url and\
            'programas/' not in redirect_soup._url and 'juegos-para-pc/' not in redirect_soup._url\
            and 'android/' not in redirect_soup._url and 'cursos/' not in redirect_soup._url and\
                        '403' not in redirect_soup.title and 'members/' not in redirect_soup._url:
            title = redirect_soup.select_one('h1').text
            redirect_links = redirect_soup.find_all('a', text=u'VER ENLACES')
            for redirect_link in redirect_links:
                play_soup = self.get_soup(redirect_link['href'])
                play_links = play_soup.select('div.post-contenido a')
                for play_link in play_links:
                    self.submit_parse_result(
                        index_page_title=self.util.get_page_title(redirect_soup),
                        link_url=play_link.text,
                        link_text=title,
                    )
            for play_urls in redirect_soup.select('a.goto')+redirect_soup.select('a.descargar'):
                data = {'mirror': play_urls['data-id']}
                play_soup = self.post_soup('http://www.programasgratisfull.com/goto/', data=data)
                play_link = play_soup.select_one('a')
                if play_link:
                    self.submit_parse_result(
                        index_page_title=self.util.get_page_title(redirect_soup),
                        link_url=play_link['href'],
                        link_text=title,
                    )
            for season_link in redirect_soup.select('dl.lista-capitulos a'):
                self.parse(season_link.href)
