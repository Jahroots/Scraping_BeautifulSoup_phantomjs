#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class GidOnlineClub(SimpleScraperBase):

    BASE_URL = 'http://gidonline.in'
    OTHER_URLS = ['http://gidonline.club']

    LONG_SEARCH_RESULT_KEYWORD = u'они'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return u'Ничего не найдено по запросу'

    def _fetch_next_button(self, soup):
        link = soup.find('a', text='>')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        # This site redirects to the actual result if there's only one.
        # Check for any results; if none, submit myself.
        results = soup.select('a.mainlink')
        for result in results:
            img = result.find('img')
            image = link_title = None
            if img:
                image = img['src']
                link_title = img['alt']

            self.submit_search_result(
                link_url=result['href'],
                link_title=link_title,
                image=self.BASE_URL + image,
            )

        if not results:
            # see if we have a canonical link, and use that as as search result
            can = soup.find('link', attrs={'rel': 'canonical'})
            if can:
                self.submit_search_result(
                    link_url=can['href']
                )
            else:
                self.submit_search_no_results()

    def __extract_iframe(self, soup, **kwargs):
        for iframe in soup.select('div.tray iframe'):
            src = iframe['src']
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url='http:' + src if src.startswith('//') else src,
                                     **kwargs
                                     )

    def _parse_parse_page(self, soup):
        # Ugh, this one was a hog.
        # There is a post back to 'trailer.php'.  A 2 hour long trailer. :|
        # It takes id_post as a parameter found in
        # <meta id="meta" content="19546" />
        meta = soup.find('meta', {'id': 'meta'})
        if meta:
            id_post = meta['content']
            trailer = self.post_soup(self.BASE_URL + '/trailer.php',
                data={'id_post': id_post})

            for iframe in trailer.select('iframe'):
                src = iframe['src']
                self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                         link_url='http:' + src if src.startswith('//') else src,
                                         )

        self.__extract_iframe(soup)

