# coding=utf-8
import time
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class VeehdCom(SimpleScraperBase):
    BASE_URL = 'http://veehd.com'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    LONG_SEARCH_RESULT_KEYWORD = '2015'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(VeehdCom, self).get(url, **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search?q={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('table.movieList h2 a'):
            result = self.BASE_URL+results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            found=1
        if not found:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)

        title = soup.select_one('div#videoName h2')
        if title:
            title = title.text.strip()
        else:
            title = soup.select_one('div.data h1').text.strip()


        iframe = soup.select_one('div.movieplay iframe')
        if iframe and iframe.has_attr('src'):
            if iframe['src']:
                self.log.warning(iframe['src'])
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe['src'],
                    link_text=title,
                )
                return


        source_url = soup.text.split('src : "')[-1].split('"});')[0]

        movies_soup = self.get_soup('http://veehd.com'+source_url)
        wait_text = ''
        try:
            wait_text = movies_soup.find(text=re.compile('Wait 5 minutes'))
        except AttributeError:
            pass
        if wait_text:
            self.log.debug('wait 5 minutes')
            time.sleep(301)
            movies_soup = self.get_soup('http://veehd.com' + source_url)
            movie_link = movies_soup.find('h2')
            if movie_link:
                movie_link = movie_link.find_next('span')
                if movie_link:
                    movie_link = movie_link.find('a')['href']
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link,
                        link_text=title,
                    )
        else:
            movie_link = movies_soup.find('h2')
            if movie_link:
                movie_link = movie_link.find_next('span')
                if movie_link:
                    movie_link = movie_link.find('a')['href']

                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link,
                        link_text=title,
                    )