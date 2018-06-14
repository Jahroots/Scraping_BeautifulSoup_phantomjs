# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class DiziizleNet(SimpleScraperBase):
    BASE_URL = 'https://www.diziizle.net'
    OTHER_URLS = ['http://www.diziizle.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    SINGLE_RESULTS_PAGE = True

    def get(self, url, **kwargs):
        return super(DiziizleNet, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return u'{}/?ara={}'.format(self.BASE_URL, self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Aradığınız Kriterlere Uygun Kayıt Bulunamadı'

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.film'):
            link = result.select_one('a.mavi-ok')
            if 'Dizi izle' in link.href:
                # we're a series - follow the link and submit episodes.
                series_soup = self.get_soup(link.href)
                image = self.util.find_image_src_or_none(result, 'img')
                for link in series_soup.select('div.film div.resim a'):
                    self.submit_search_result(
                        link_url=self.BASE_URL + '/' + link.href,
                        link_title = link.text,
                        image=image
                    )
            else:
                self.submit_search_result(
                    link_url=self.BASE_URL + '/' + link.href,
                    link_title=link.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for iframe in soup.select('div#video_ekran div.video_ekran_player iframe'):
            url = iframe['src']
            if url.startswith('//'):
                url = 'http:' + url
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=url,
                series_season=series_season,
                series_episode=series_episode,
            )
