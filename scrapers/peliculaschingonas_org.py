# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class PeliculaschingonasOrg(SimpleScraperBase):
    BASE_URL = 'https://www.peliculaschingonas.org'
    OTHER_URLS = ['http://www.peliculaschingonas.org', ]
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'esp'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'»')
        if link:
           return link['href']

    def _parse_search_result_page(self, soup):
        find = 0
        for results in soup.select('div.title h3 a'):
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            find=1
        if not find:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h3.post-title a').text.strip()
        index_page_title = self.util.get_page_title(soup)
        input = soup.find('div', 'entry').find('input')
        if input:
            movie_links = input.find_next('center').find_all('iframe')

            for movie_link in movie_links:
                video_soup = self.get_soup(movie_link['src'], allowed_errors_codes=[404])
                video_iframe_links = video_soup.find('div', id='TabbedPanels1')
                if video_iframe_links:
                    video_iframe_links = video_iframe_links.find_all('iframe')
                    for video_iframe_link in video_iframe_links:
                        if video_iframe_link.has_attr('src'):
                            video_link = video_iframe_link['src']
                            self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=video_link,
                                link_text=title,
                            )

                video_a_links = video_soup.find('div', id='TabbedPanels1')
                if video_a_links:
                    video_a_links = video_a_links.find('div', 'TabbedPanelsContentGroup').find_all('a')
                    for video_a_link in video_a_links:
                        self.submit_parse_result(
                            index_page_title=index_page_title,
                            link_url=video_a_link['href'],
                            link_text=title,
                        )
