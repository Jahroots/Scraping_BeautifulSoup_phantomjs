# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import base64


class MozicsillagCc(SimpleScraperBase):
    BASE_URL = 'http://mozicsillag.me'
    OTHER_URLS = ['http://mozicsillag.cc', ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'hun'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_no_results_text(self):
        return u'Nem ezeket keresed?'

    def get(self, url, **kwargs):
        return super(MozicsillagCc, self).get(
            url, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        link_pattern = 'search_term={}&search_type=0&search_where=0&search_rating_start=1&search_rating_end=10&search_year_from=1900&search_year_to=2016'.format(self.util.quote(search_term))
        encode_link_pattern = base64.b64encode(link_pattern)
        return self.BASE_URL + '/kereses/{}'.format(encode_link_pattern)

    def _fetch_next_button(self, soup):
        return soup.find('ul', 'pagination').find('a', text=u'»')['href']

    def _parse_search_result_page(self, soup):
        for search_link in soup.select('ul[class="small-block-grid-2 medium-block-grid-4 large-block-grid-5 enable-hover-link"] li a'):
            link = search_link['href']
            title = search_link.find('h2').text.strip().encode('utf-8')
            self.submit_search_result(
                    link_url=link,
                    link_title=title,
                )


    def _parse_parse_page(self, soup):
        video_link = soup.find('a', text="Beküldött linkek megtekintése")
        title = self.util.get_page_title(soup)
        page_url = video_link['href']
        source_soup = self.get_soup(page_url)
        panels = source_soup.find_all('div', 'panel')
        for panel in panels:
            watch_url = panel.find('div', 'link_play').find_previous('a')['href']
            movie_url = self.get_redirect_location('http://filmbirodalmak.com'+'/'+watch_url)
            self.submit_parse_result(index_page_title=title,
                                     link_url=movie_url)
