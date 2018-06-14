# coding=utf-8
import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class VideogetMe(SimpleScraperBase):
    BASE_URL = 'http://videoget.me'

    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"
        raise NotImplementedError('The website is out of reach')

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL,
        )
        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)



    def _fetch_no_results_text(self):
        return 'your search did not yield any results'


    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?keywords=' + self.util.quote(search_term)

    def _fetch_next_button(self, soup):
        link = soup.find('a', text=u'»')
        return self.BASE_URL + '/'+ link['href'] if link else None


    def _parse_search_result_page(self, soup):
        for result in soup.select('.pm-li-video'):
            title_link = result.select_one('h3 a')
            title = result.select_one('h3').text
            self.submit_search_result(
                link_url=title_link['href'],
                link_title=title,
            )


    def parse(self, parse_url, **extra):
        soup = self.get_soup(parse_url)

        title = soup.find('h1', 'entry-title').text
        season, episode = re.search('(\d)+x(\d+)', title).group(1), re.search('(\d)+x(\d+)', title).group(2)
        index_page_title = self.util.get_page_title(soup)

        for script in soup.select('script'):
            if 'var pm_video_data =' in script.text:
                json_data = script.text.split('var pm_video_data =')[1].strip()
                url = json_data.split('embed_url:')[1].split(',')[0].replace('"','')
                soup = self.get_soup(url)

                for script in soup.select('script'):
                    if 'player.src([{src:' in script.text:
                        url = script.text.split('player.src([{src:')[1].split(',')[0].replace('"','').strip()
                        self.submit_parse_result(index_page_title = index_page_title,
                                         series_season = season,
                                         series_episode = episode,
                                         link_url = url
                                         )

