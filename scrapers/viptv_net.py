# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ViptvNet(SimpleScraperBase):
    BASE_URL = 'http://viptv.net'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]
    SINGLE_RESULTS_PAGE = True
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search_list.php?keyword_main={search_term}&type=0'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('a.text-list'):
            link = result.href
            self.submit_search_result(
                link_url=link,
                link_title=result.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
            found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h5')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(soup._url)
        script_text = ''
        try:
            script_text = soup.find('script', text=re.compile("jwplayer.key")).find_next('script').text
        except AttributeError:
            pass
        urls = re.search("""ajax\(\{url:\"/movieplay_size(.*)\",""", script_text)
        if urls:
            redirect_url = self.BASE_URL+'/movieplay_size'+urls.groups()[0]
            movie_links = self.get(redirect_url).text.split('|')
            for movie_link in movie_links:
                if movie_link:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link,
                        link_title=movie_link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
        other_links = self.util.find_urls_in_text(script_text)
        for other_link in other_links:
            if 'mp4?url=' in other_link:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=other_link,
                    link_title=other_link,
                    series_season=series_season,
                    series_episode=series_episode,
                )
