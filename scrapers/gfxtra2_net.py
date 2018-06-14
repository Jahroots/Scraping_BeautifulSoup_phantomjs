# coding=utf-8
import base64
import urllib

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Gfxtra2Net(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'https://www.gfxtra02.com'
    OTHER_URLS = ['https://www.gfxtra10.com']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        for url in (self.BASE_URL,
                    'https://www.gfxtraz.com',
                    'http://www.gfxtram.com',
                    'http://www.gfxttra.com',
                    'http://www.gfxtray.com',
                    'http://www.gfxtr.net/',
                    'http://www.gfxtra3.net',
                    'http://www.gfxtr.net',
                    'http://www.gfxtr2.com',
                    'http://www.gfxxtra.com',
                    'http://www.gfxtrra.com',
                    'https://www.gfxta.com'):
            self.register_url(
                ScraperBase.URL_TYPE_SEARCH,
                url)

            self.register_url(
                ScraperBase.URL_TYPE_LISTING,
                url)

    def _fetch_no_results_text(self):
        return 'The search did not return any results.'

    def _search_with_get(self):
        return True

    def _parse_search_result_page(self, soup):
        for result in soup.select('div#mcontent_inner_box'):
            # content_inner_box is a generic id used many times; only get
            #  those with a aciklama link
            article = result.select('div.article')
            title = result.select('div.aciklama a')
            if not article or not title:
                continue
            title_link = title[0]

            asset_type = None
            details = result.select('div.detay')
            if details:
                details_text = details[0].text
                if details_text.find('Movies'):
                    asset_type = ScraperBase.MEDIA_TYPE_FILM
                elif details_text.find('TV'):
                    asset_type = ScraperBase.MEDIA_TYPE_TV

            image = None
            img = result.select('div.article img')
            if img:
                image = img[0]['src']
            self.submit_search_result(
                link_url=title_link['href'],
                link_title=title_link.text,
                asset_type=asset_type,
                image=image,
            )

    def _parse_parse_page(self, soup):
        # Pretty open format - grab any line starting with http in a quote.
        found = set()
        for quotebox in soup.select('div.article div.quote'):
            for url in self.util.find_urls_in_text(str(quotebox)):
                if url in found:
                    continue
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=url
                                         )
                found.add(url)

        for link in soup.select('div.article a'):
            if '/engine/go.php?url=' in link.href:
                href = base64.urlsafe_b64decode(urllib.unquote(link.href.split('/engine/go.php?url=')[1]))
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=href
                                         )
                found.add(href)
