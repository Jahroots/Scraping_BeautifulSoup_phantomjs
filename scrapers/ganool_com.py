# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class GanoolCom(SimpleScraperBase):
    BASE_URL = 'https://ganool.ac'
    OTHER_URLS = ['https://ettv.st', 'https://ganool.se', 'https://cmovieshd.se', 'http://cmovieshd.se',
                  'http://ganool.ee',
                  'https://ganool.st', 'https://goody.to', 'https://ganool.sc', 'https://ganool.is', 'https://ganool.li', 'https://goon.to']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for site in [self.BASE_URL]+ self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, site)
            self.register_url(ScraperBase.URL_TYPE_LISTING, site)


    def get(self, url, **kwargs):
        return super(GanoolCom, self).get(url, verify=False, **kwargs)


    def _fetch_no_results_text(self):
        return 'Sorry, but nothing matched your search'


    def _fetch_next_button(self, soup):
        link = soup.find ('a', text= u'Next')
        if link:
            return link['href']


    def _parse_search_result_page(self, soup):
        results = soup.select('.ml-mask h2')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in soup.select('.ml-mask'):
            title_link = result.select_one('h2').text
            # first image in summary
            image = None
            img = result.select_one('.thumb.mli-thumb')
            if img:
                image = img.attrs['style'][22:-1]

            self.submit_search_result(
                link_url=result['href'],
                link_title=title_link,
                image=image
            )


    def _parse_parse_page(self, soup):
        img = soup.select_one('.img-responsive')

        # Find all links that aren't subtitles or imdb.
        for link in soup.select('.table.table-bordered tr td a'):
            if self.util.check_for_strings(link['href'],
                                           ('http://ganool.com', 'imdb.com', 'subscene.com')):
                continue

            if link.select('img'):
                # Skip image links...
                continue

            if link.startswith_http:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=link['href'],
                                         link_title=link.text,
                                         image=img['src']
                                         )
