# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class Fullmovie2in(SimpleScraperBase):
    BASE_URL = 'http://www.fullmovie2in.eu'
    OTHER_URLS = ['http://www.fullmovie2in.net']

    LONG_SEARCH_RESULT_KEYWORD = 'rock'
    SINGLE_RESULTS_PAGE = True

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)
        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        for url in [self.BASE_URL, ] + self.OTHER_URLS:
            self.register_url(ScraperBase.URL_TYPE_SEARCH, url)
            self.register_url(ScraperBase.URL_TYPE_LISTING, url)

    def _fetch_no_results_text(self):
        return 'Sorry, but nothing matched your search criteria'

    def _fetch_next_button(self, soup):
        return

    def _parse_search_result_page(self, soup):
        results = soup.select('.boxed.film a')
        if not results:
            self.submit_search_no_results()

        for result in results:
            self.submit_search_result(link_title=result['title'],
                                      link_url=result.href)

    def _parse_parse_page(self, soup, depth=0):
        title = soup.select_one('.entry-title').text.replace(' Full Movie Watch Online Now Free', '')
        season, episode = self.util.extract_season_episode(title)
        for page_link in soup.select('.entry-content div p a'):
            page_url = page_link.href
            if page_url.startswith('http://embed.linkembed.biz/emb'):
                api_page = self.get(page_url)
                api_num = api_page.content.split('dax =')[-1].split(';')[0].strip().replace('"', '')
                #video_url = page_url.replace('video.php', 'ajax/player.php')

                video_url = 'http://embed.linkembed.biz/embed/app/dashboard/player.php?'+'api='+api_num

                iframe_video_page = self.get_soup(video_url).select_one('iframe')
                if iframe_video_page:
                    movie_link = iframe_video_page['src']
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=movie_link,
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode)
                a_video_page = self.get_soup(video_url).select_one('a')
                if a_video_page:
                    movie_link = a_video_page['href']
                    self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                             link_url=movie_link,
                                             link_title=title,
                                             series_season=season,
                                             series_episode=episode)
                ad_video_page = self.get_soup(video_url).select_one('meta[http-equiv="refresh"]')
                if ad_video_page:
                    continue
                # base_video_link = base_video_page.text.split('fast = ')[-1].split(';')[0].strip().replace('"', '')
                # id_num =base_video_page.text.split('Seconds = ')[-1].split(';')[0].strip().replace('"', '')
                # if not base_video_link or not id_num:
                #     continue
                # video_link = base_video_link+id_num
                # try:
                #     self.submit_parse_result(index_page_title=soup.title.text.strip(),
                #                              link_url=movie_link,
                #                              link_title=title,
                #                              series_season=season,
                #                              series_episode=episode)
                # except IndexError:
                #     pass  # self.log.warning(soup2.select('iframe'))
