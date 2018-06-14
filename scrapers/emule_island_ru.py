#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class EmuleIslandRu(SimpleScraperBase):

    BASE_URL = 'http://www.emule-island.ru'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "fra"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + \
            '/recherche.php?categorie=99&rechercher=Search&' + \
            'find=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return u'0 fiche(s) trouvée(s)'

    def _fetch_next_button(self, soup):
        right_img = soup.find('img',
            {'src': 'http://cdn.emule-island.ru/images/gotoright.gif'})
        if right_img:
            return self.BASE_URL + right_img.parent['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.fiche_listing'):
            link = result.find('a', 'titre_fiche')
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text.strip(),
                image=self.util.find_image_src_or_none(soup, 'img.thumb')
            )

    def _parse_parse_page(self, soup):
        # This is a bit broken - there are links to 'sister' sites.
        # Just spit them out.
        for klass in ('ddl', 'stream'):
            link = soup.find('a', klass)
            if link:
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link['href']
                                         )

