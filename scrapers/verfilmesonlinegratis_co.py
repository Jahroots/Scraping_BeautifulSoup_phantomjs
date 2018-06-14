from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import CloudFlareDDOSProtectionMixin, SimpleScraperBase
import re
import base64

class VerFilme(SimpleScraperBase):
    BASE_URL = 'https://www.masterfilmesonline.net'
    OTHER_URLS = ['https://www.verfilmesonlinegratis.co','http://www.verfilmesonlinegratis.co']

    def setup(self):
        raise NotImplementedError('Deprecated. Site suspended.')
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'por'
        #raise NotImplementedError("The CF recap is solved but after that the website return time out error")
        self.requires_webdriver = True
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)


    def _fetch_no_results_text(self):
        return 'No results to show'

    def _fetch_next_button(self, soup):
        link = soup.select_one('div.resppages a')
        self.log.debug('------------------------')
        return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('div.result-item')

        if not results or len(results)==0:
            return self.submit_search_no_results()

        for result in results:
            link = result.select_one('div.title a')

            if not link:
                continue

            self.submit_search_result(
                link_url= link['href'],
                link_title=link.text
            )

    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)
        title = soup.select_one('h1').text

        iframe = soup.select_one('iframe[src*="verfilmesonlinegratis.co"]')
        if iframe and iframe['src']:
            self.log.debug(iframe)
            soup1 = self.get_soup(self.format_iframe(iframe['src']))
            code = str(soup1.select('script')[8])

            for link in re.findall('addiframe.*\)', code):
                link = link.replace('addiframe(\'','').replace('\')', '')
                self.log.debug(link)
                if link != 'addiframe(URL)':
                    self.submit_parse_result(
                        index_page_title=self.util.get_page_title(soup),
                        link_url=link,
                        link_title=title
                    )
        else:
            iframes = soup.select('iframe[class="metaframe rptss"]')
            for iframe in iframes:
                link = iframe['src']
                link = base64.decodestring(link.split('show=')[1])
                if link != 'addiframe(URL)':
                    self.submit_parse_result(
                        index_page_title=self.util.get_page_title(soup),
                        link_url=link,
                        link_title=title

                    )

