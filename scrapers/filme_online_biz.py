# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, ScraperParseException

class FilmeOnlineBiz(SimpleScraperBase):
    BASE_URL = 'http://filmeonline.to'
    OTHER_URLS = ['http://www.filme-online.biz', ]
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ron'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def search(self, search_term, media_type, **extra):
        page_soup = self.get_soup(self.BASE_URL)
        token_input = page_soup.select_one('input[name="_token"]')
        if not token_input:
            raise ScraperParseException("Could not find token.")
        data = {
                '_token': token_input['value'],
                'search_term': search_term,
                'search_type':0,
                'search_where':0,
                'search_rating_start':1,
                'search_rating_end':10,
                'search_year_from':1900,
                'search_year_to':2017
            }
        soup = self.post_soup(
            self.BASE_URL + '/filme-online/filtrare',
            data=data,
        )

        self._parse_search_results(soup)

    def _fetch_no_results_text(self):
        return u'Sunt 0 Resultados'

    def _fetch_next_button(self, soup):
        for button in soup.select('li.arrow a'):
            if button.href and button.href.startswith('http'):
                return button.href
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.columns ul.enable-hover-link li'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for iframe in soup.select('div.flex-video iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe['src'],
                series_season=series_season,
                series_episode=series_episode,
            )
