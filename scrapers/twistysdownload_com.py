# -*- coding: utf-8 -*-

from sandcrawler.scraper import OpenSearchMixin
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import SimpleScraperBase


class TwistysDownloadCom(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://www.twistysdownload.com'

    LONG_SEARCH_RESULT_KEYWORD = 'super'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_ALL)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'The search did not return any results.'

    def _parse_search_result_page(self, soup):
        # Ugly html...
        # Find dle-content's parent, then find all tables with an ntitle
        dle_content = soup.select_one('div#dle-content')
        if not dle_content:
            raise ScraperParseException('Could not find dle-content')
        for table in dle_content.parent.children:
            if table.name != 'table':
                continue
            ntitle = table.select_one('span.ntitle')
            if not ntitle:
                continue
            readmore = table.find('strong', text='Read More')
            if not readmore:
                continue
            link = readmore.parent
            self.submit_search_result(
                link_url=link['href'],
                link_title=ntitle.text,
            )

    def _parse_parse_page(self, soup):
        content = soup.select('div#dle-content table > tr > td > div')
        if content:
            image = self.util.find_image_src_or_none(content[0], 'img')
            for link in self.util.find_urls_in_text(str(content[0]),
                skip_images=True):
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url=link,
                                         image=image,
                                         )
