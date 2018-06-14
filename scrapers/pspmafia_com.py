# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import SimpleScraperBase


class PSPMafiaCom(SimpleScraperBase):
    BASE_URL = 'http://pspmafia.com'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'Unfortunately your search didn\'t return any results.'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/index.php?type=All&q=' + search_term

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='Next >>')
        return self.BASE_URL + link['href'] if link else None

    def _parse_search_result_page(self, soup):
        results = False

        for result in soup.select('div#ucpcontent table.ipbtable tr'):
            # make sure we have a movie or tv icon
            if result.find('img', {'title': 'movie'}) or \
                    result.find('img', {'title': 'tv'}):
                link = result.select_one('a')
                self.submit_search_result(
                    link_url=self.BASE_URL + '/' + link['href'],
                    link_title=link.text
                )
                results = True
        if not results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        # grab the main frame
        mainframe = soup.select_one('frame#mainFrame')
        if not mainframe:
            raise ScraperParseException('Failed to find frame')
        frame_soup = self.get_soup(mainframe['src'])
        if unicode(frame_soup).find(
                'seems to be out of date or broken.') >= 0:
            self.log.warning('404 from search result.')
            return

        body = frame_soup.select('td.post2 div.postcolor')
        if not body:
            raise ScraperParseException('Could not find body')
        body = body[0]
        image = self.util.find_image_src_or_none(body, 'img')
        for link in self.util.find_urls_in_text(
                unicode(body),
                skip_images=True,
                skip_imdb=True,
                skip_youtube=True,
        ):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=link,
                                     image=image,
                                     )
