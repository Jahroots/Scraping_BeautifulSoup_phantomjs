# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase, ScraperParseException
from sandcrawler.scraper.caching import cacheable
import re

class EgfireCom(SimpleScraperBase):
    BASE_URL = 'http://egfire.com'
    OTHER_URLS = ['http://www.egfire.com']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'ara'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ScraperBase.MEDIA_TYPE_BOOK, ScraperBase.MEDIA_TYPE_GAME, ScraperBase.MEDIA_TYPE_OTHER, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = '2016'
    TRELLO_ID = 'gNQpvUVJ'


    def _fetch_search_url(self, search_term, media_type):
        return u'{}/?s={}&search=search'.format(self.BASE_URL, search_term)

    def _fetch_no_results_text(self):
        return u'عذرا - لم يتم العثور على ما يطابق بحثك. حاول بطريقة اخرى.'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a[class="next page-numbers"]')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        results = soup.select('article.post div.boxes a')
        if not results and len(results) == 0:
            return self.submit_search_no_results()

        for result in results:
            # Open the link - there's a click to download (a link to a forum)
            # and a click to watch (streaming)
            result_soup = self.get_soup(result.href)
            for path in ('div.btnDown a', 'div.btnView a'):
                link = result_soup.select_one(path)
                if link and link.href:
                    self.submit_search_result(
                        link_url=link.href,
                        link_title=result['title'],
                    )

    @cacheable()
    def _follow_short_link(self, url):
        # follow it.
        short_soup = self.get_soup(url)
        for link in short_soup.select('a'):
            if link.href.startswith('m1.php'):
                url = u'http://www.short.egfire.com/{}'.format(link.href)
                getlink_soup = self.get_soup(url)
                input = getlink_soup.select_one('input[name="groovybtn1"]')
                if input:
                    return [u for u in self.util.find_urls_in_text(str(input))]
        return []

    def _get_server(self, post_id, link_id):
        result = self.get_soup(
            u'http://egfire.com/wp-content/themes/3arbServ/inc/temp/data/video.php?id={}&video={}'.format(
                post_id,
                link_id,
            ),
            headers={
                'X-Requested-With': 'XMLHttpRequest',
            }
        )
        results = []
        for iframe in result.select('iframe'):
            results.append(iframe['src'])
        return results

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        title = soup.select_one('h1').text
        links = soup.select('div.btnView a')
        for link in links:
            soup = self.get_soup(link.href)
            for a in soup.select('ul.downloads a'):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=a.href,
                    link_title=link.text,
                )

        iframe = soup.select_one('div.getCode iframe')
        self.submit_parse_result(
            index_page_title=index_page_title,
            link_url= iframe['src'],
            link_title= title,
        )





