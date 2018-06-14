# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class PutlockerOnline(SimpleScraperBase):
    BASE_URL = 'http://putlocker.online'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def setup(self):
        raise NotImplementedError('Website Not Available')

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?&s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Apologies, but no results were found'

    def _fetch_next_button(self, soup):
        next_button = soup.select_one('a.next')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.thumb'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for link in soup.select('div#video iframe'):
            mirrors_links = link['src']+'?source=a1'
            if '/movie/mystery-woman' in mirrors_links or 'eugene-mirman-vegan' in mirrors_links:
                continue
            mirrors_soup = self.get_soup(mirrors_links)
            iframe_links = None
            try:
                iframe_links = self.util.find_urls_in_text(mirrors_soup.select_one('div.wInnerBall').find_next('script').text.split('source src=')[-1])
            except AttributeError:
                pass
            if iframe_links:
                for iframe_link in iframe_links:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=iframe_link,
                        link_title=iframe_link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
            js_text = mirrors_soup.find('body').find_all('script')[-1].text
            while 'http' in js_text:
                script_source = self.util.find_urls_in_text(mirrors_soup.find('body').find_all('script')[-1].text)
                for mirrors_links in script_source:
                    if not mirrors_links:
                        break
                    mirrors_soup = self.get_soup(mirrors_links)
                    iframe_links = None
                    try:
                        iframe_links = self.util.find_urls_in_text(
                            mirrors_soup.select_one('div.wInnerBall').find_next('script').text.split('source src=')[-1])
                    except AttributeError:
                        pass
                    if iframe_links:
                        for iframe_link in iframe_links:
                            self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=iframe_link,
                                link_title=iframe_link,
                                series_season=series_season,
                                series_episode=series_episode,
                            )
                    js_text = mirrors_soup.find('body').find_all('script')[-1].text
            else:
                mirrors_links = link['src'] + '?source=a{}'.format(int(mirrors_links[-1])+1)
                mirrors_soup = self.get_soup(mirrors_links)
                iframe_link = mirrors_soup.select_one('iframe')['src']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=iframe_link,
                    link_title=iframe_link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
