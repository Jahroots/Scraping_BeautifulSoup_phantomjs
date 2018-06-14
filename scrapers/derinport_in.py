# -*- coding: utf-8 -*-

import time

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Derinport(SimpleScraperBase):
    BASE_URL = 'http://derinport.in'

    LONG_SEARCH_RESULT_KEYWORD = '2016'
    USER_AGENT_MOBILE = False

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'tur'

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_OTHER)
        self.register_media(ScraperBase.MEDIA_TYPE_GAME)
        self.register_media(ScraperBase.MEDIA_TYPE_BOOK)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_no_results_text(self):
        return None #u'Sorry - no matches. Please try some different terms.'
        # return u'Arama kriterine uygun sonuç bulunamadi, Lütfen baska bir Arama kriteri (Aranacak Kelime) vererek tekrar deneyin.'

    def search(self, search_term, media_type, **extra):
        self.search_term = search_term
        self.media_type = media_type

        self.get(self.BASE_URL + '/search.php?search_type=1&langid=1')
        soup = self.post_soup(
                self.BASE_URL + '/search.php?do=process',
                data=[('type[]', ''), ('type[]', '3'), ('type[]', '1'), ('type[]', '7'), ('type[]', '5'),
                      ('type[]', '11'), ('type[]', '20'), ('type[]', '19'), ('query', search_term), ('titleonly', '1'),
                      ('searchuser', ''),  # ('starteronly', '0'),
                      ('tag', ''), ('forumchoice[]', ''), ('childforums', '1'),
                      # ('prefixchoice[]', ''),
                      # ('prefixchoice[]', 'Film'),
                      # ('prefixchoice[]', 'Dizi'),
                      # ('prefixchoice[]', 'Oyun'),
                      # ('prefixchoice[]', 'Program'),
                      ('replyless', '0'), ('replylimit', ''), ('searchdate', '0'),
                      ('beforeafter', 'after'), ('s', ''),
                      ('sortby', 'dateline'), ('order', 'descending'), ('showposts', '0'),
                      ('dosearch', 'Search Now'),
                      ('searchthreadid', ''), ('s', ''), ('securitytoken', 'guest'),
                      # ('searchfromtype', 'vBForum, Post'),
                      ('do', 'process'),
                      # ('contenttypeid', '1')
                      ]
            )


        self._parse_search_results(soup)

    def _fetch_next_button(self, soup):
        next = soup.find('a', rel='next')

        self.log.debug('------------------------')
        return self.BASE_URL + '/' + next['href'] if next else None

    def _parse_search_result_page(self, soup):
        #self.log.debug(soup)

        if 'This forum requires that you wait' in str(soup):
            self.log.debug('sleeping...')
            time.sleep(int(str(soup).split('again in ')[1].split(' seconds')[0]) + 3.33)
            return self.search(self.search_term, self.media_type)


        results = soup.select('a[id*="thread_title"]')
        if not results or len(results) == 0:
            return self.submit_search_no_results()

        for link in soup.select('a[id*="thread_title"]'):
            self.submit_search_result(
                link_url=self.BASE_URL + '/' + link['href'],
                link_title=link.text,
            )


        next_button = self._fetch_next_button(soup)
        if next_button and self.can_fetch_next():
            soup = self.get_soup(next_button)
            self._parse_search_result_page(soup)


    def parse(self, parse_url, **extra):

        # There's some stuff int he header breaking beautifulsoup... :(
        contents = self.get(parse_url).text
        contents = contents[contents.find('body'):]
        soup = self.make_soup(contents)

        index_page_title = self.util.get_page_title(soup)

        title = soup.select_one('.title.icon')
        season = episode = None

        if title and title.text:
            title = title.text
            season, episode = self.util.extract_season_episode(title)

        submitted = set()
        items = soup.select('div.content') + soup.select('.bbcode_code div')

        for item in items:
            for link in self.util.find_urls_in_text(item.text):
                if link not in submitted:
                    self.submit_parse_result(index_page_title=index_page_title,
                                             link_url=link,
                                             series_season=season,
                                             series_episode=episode
                                             )
                    submitted.add(link)

        for link in soup.select('.bbcode_code code code'):
            link = link.text.strip()
            if link not in submitted:
                self.submit_parse_result(index_page_title=index_page_title,
                                         link_url=link,
                                         series_season=season,
                                         series_episode=episode
                                         )
                submitted.add(link)

        for link in soup.select('.postcontent.restore div a'):
            if not link.href.startswith(self.BASE_URL) and 'imdb.com/' not in link.href:
                if link.href not in submitted:
                    self.submit_parse_result(index_page_title=index_page_title,
                                             link_url=link.href,
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode
                                             )
                    submitted.add(link.href)

