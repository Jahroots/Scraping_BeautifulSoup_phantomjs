# coding=utf-8
import json
from sandcrawler.scraper import ScraperBase, SimpleScraperBase

class ZumvoSo(SimpleScraperBase):
    BASE_URL = 'http://www.zumvo.so'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    LONG_SEARCH_RESULT_KEYWORD = 'the'


    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/search/{search_term}/'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text='Last')
        if next_button:
            return next_button['href']
        else:
            return None

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('div[class="movies-list movies-list-full"] div.ml-item a.ml-mask'):
            soup = self.get_soup(result.href)
            result = soup.select_one('div.icon-play a')
            if result:
                self.submit_search_result(
                        link_url=result.href,
                        link_title=result['title'],
                        image= self.util.find_image_src_or_none(result, 'img')
                    )
                found=1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):

        series_season = series_episode = None

        post_player = self.BASE_URL + '/load_player'
        for episode in soup.select('#list-episode a'):
            soup = self.get_soup(episode.href)
            index_page_title = self.util.get_page_title(soup)

            for script in soup.select('script'):
                if 'episodeID =' in script.text:

                    episodeID = script.text.split("episodeID")[1].split("')")[0].replace("= parseInt('",'')
                    filmID = script.text.split("filmID")[1].split("')")[0].replace("= parseInt('",'')

                    soup = self.post_soup(post_player, data = {'NextEpisode' : 1,
                                                        'EpisodeID' : episodeID,
                                                        'filmID' : filmID})
                    if not 'http' in soup.text:
                        continue

                    xml = soup.text.split('var url_playlist = "')[1].split('";')[0].strip()
                    soup = self.get_soup(xml)
                    title = soup.select_one('title').text
                    series_season, series_episode = self.util.extract_season_episode(title)
                    series_episode = soup.select_one('item title').text


                    for url in self.util.find_urls_in_text(unicode(soup.select_one('item'))):
                            self.submit_parse_result(
                                index_page_title=index_page_title,
                                link_url=url,
                                link_title=title,
                                series_season=series_season,
                                series_episode=series_episode,
                            )
