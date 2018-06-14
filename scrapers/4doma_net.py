# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class FourdomaNet(SimpleScraperBase):
    BASE_URL = 'http://1doma.tv'
    OTHER_URLS = ['http://4doma.net']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search/?q={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Nothing Found'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text=u'»')
        if next_button:
            return 'http:'+next_button.href
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div.film'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h2')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        flash_link = ''
        try:
            flash_link = soup.find('param', attrs={'name':'flashvars'})['value']
        except TypeError:
            pass
        if flash_link:
            if '&pl=' in flash_link:
                flash_link = flash_link.split('&pl=')[-1]
                flash_soup = self.get_soup(flash_link)
                for link in self.util.find_file_in_js(flash_soup.text):
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link,
                        link_title=link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
            elif '&file=' in flash_link:
                flash_link = flash_link.split('&file=')[-1]
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=flash_link,
                    link_title=flash_link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
        script_links = ''
        try:
            js = unicode(soup.find('div', 'player').find_next('script'))
            script_links = self.util.find_file_in_js(js)
        except AttributeError:
            pass
        if script_links:
            for script_link in script_links:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=script_link,
                    link_title=script_link,
                    series_season=series_season,
                    series_episode=series_episode,
                )

        for iframe_link in soup.select('div.content iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe_link['src'],
                link_title=iframe_link.text,
                series_season=series_season,
                series_episode=series_episode,
            )