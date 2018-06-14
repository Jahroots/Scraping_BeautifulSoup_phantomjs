#coding=utf-8

from sandcrawler.scraper import ScraperBase, \
    CloudFlareDDOSProtectionMixin, \
    SimpleScraperBase
import re
from sandcrawler.scraper.caching import cacheable

class DDLWarezIn(CloudFlareDDOSProtectionMixin, SimpleScraperBase):

    BASE_URL = 'https://ddl-warez.to/'
    OTHER_URLS = ['http://ddl-warez.in', ]
    LANGUAGE = 'deu'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    MEDIA_TYPES = [
        ScraperBase.MEDIA_TYPE_TV,
        ScraperBase.MEDIA_TYPE_FILM
    ]
    URL_TYPES = [
        ScraperBase.URL_TYPE_SEARCH,
        ScraperBase.URL_TYPE_LISTING
    ]

    def setup(self):
        super(DDLWarezIn, self).setup()
        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_search_url(self, search_term, media_type):
        return '{}?search={}'.format(self.BASE_URL, self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'0 Ergebnisse'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = soup.select('td.no_overflow a')

        if not results or len(results)== 0:
            return self.submit_search_no_results()

        for result in results:
            self.submit_search_result(
                link_url=self.BASE_URL + result['href'],
                link_title=result.text
            )

    @cacheable()
    def _extract_links(self, id, hoster):
        results = []
        self.RECAPKEY = '6LdRRRUUAAAAAFHjnTFnBpPAUVCMhBl47IGrriLx'
        soup = self.post_soup(
            '{}download_ajax_download.php'.format(self.BASE_URL),
            data={
                'id': id,
                'download_hoster': hoster,
                'g-recaptcha-response': self.get_recaptcha_token()
            }
        )
        index_page_title = self.util.get_page_title(soup)
        for result in soup.select('table a.btn-info'):
            results.append({
                'index_page_title': index_page_title,
                'link_url': result['href'],
                'link_title': result.text,
                })
        return results


    def _parse_parse_page(self, soup):

        for button in soup.select('div#download a.btn-info'):
            span = button.parent
            if not span or span.name != 'span':
                continue

            onclick = span.get('onclick')
            srch = re.search('.val\("(.*?)"\)', onclick)
            if not srch:
                continue

            hoster = srch.group(1)

            idsrch = re.search('/download/(\d+)/', soup._url)
            if not idsrch:
                continue

            dl_id = idsrch.group(1)


            for result in self._extract_links(dl_id, hoster):
                self.submit_parse_result(**result)