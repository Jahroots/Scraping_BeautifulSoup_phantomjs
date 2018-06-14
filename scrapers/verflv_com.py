# -*- coding: utf-8 -*-

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class VerFlvCom(SimpleScraperBase):
    BASE_URL = 'http://www.ver-flv.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'esp'
        raise NotImplementedError('The website is pending deprecation')
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        raise NotImplementedError('Website not Available')

    def _fetch_no_results_text(self):
        return 'Nada encontrado.'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', class_='nextpostslink')
        if link:
            url = link['href']
            url = self.util.canonicalise(self.BASE_URL,url)
            return url
        else:
            return None

    def _parse_search_result_page(self, soup):
        any_results = False
        for result in soup.select('div.main-pelis div.box-peli'):
            link = result.select_one('h2 a')
            if not link:
                continue
            link_url = link['href']
            link_text = link.text
            image_link = self.util.find_image_src_or_none(result, 'img')
            any_results = True
            self.submit_search_result(
                link_url=link_url,
                link_title=link_text,
                image=image_link )

        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        page_title = self.util.get_page_title(soup)

        for iframe in soup.select('div.post-body iframe'):
            src = iframe.get('src', None)
            # Some pages have a blank iframe, filled with an ad via js.
            if src:
                self.submit_parse_result(index_page_title=page_title,
                                         link_url=src, )

        # This section is for download links
        for link in soup.select('a.dow1'):
            link_url = link['href']
            if 'alt' in link.attrs:
                link_title = link['alt']
            else:
                link_title = soup.select_one('.post-title.entry-title')
                if link_title:
                    link_title = link_title.text
            self.submit_parse_result(index_page_title=page_title,
                                     link_url=link_url,
                                     link_title=link_title )
