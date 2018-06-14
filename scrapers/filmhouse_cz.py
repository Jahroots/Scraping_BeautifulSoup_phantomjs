# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmhouseCz(SimpleScraperBase):
    BASE_URL = 'https://filmhouse.cz/'
    LONG_SEARCH_RESULT_KEYWORD = 'man'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "cze"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL,
        )
        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)



    def _fetch_no_results_text(self):
        return u'nebyl nalezen'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='Další filmy »')
        return next['href'] if next else None

    def _parse_search_result_page(self, soup):
        rslts = soup.find('ul', 'listing-videos listing-wall').find_all('a')
        if not rslts:
            self.submit_search_no_results()
        for result in rslts:
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title'].strip()
            )

    def _parse_parse_page(self, soup):
        meta_link = soup.find('div', 'video-embed').find('a', attrs={'href':'#'})['onclick'].split("('")[-1].split("',")[0]
        source_link = soup._url+meta_link
        source_soup=self.get_soup(source_link)
        url = None
        if source_soup.find('p') and source_soup.find('p').find('a'):
            url = source_soup.find('p').find('a')['href']
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                                 link_url=url,
                                 )
        else:
            a = soup.select_one('img.hovereff').parent.parent
            if a and a['href'] is not None:
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=a['href'],
                )
