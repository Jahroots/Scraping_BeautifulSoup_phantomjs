#coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class KStreamingCom(SimpleScraperBase):

    BASE_URL = 'https://vf.k-streaming.com'
    OTHER_URLS = ['https://www.k-streaming.com', 'http://www.k-streaming.com']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "fra"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return "n'est pas disponible."

    def _fetch_next_button(self, soup):
        link = soup.find('a','nextpostslink')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.moviefilm'):
            link = result.select('div.movief a')[0]
            image = result.find('img')['src']
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=image,
            )

    def _parse_parse_page(self, soup):
        other_links = list(
            self.get_soup_for_links(soup, 'div.keremiya_part > a')
        )
        if other_links:
            # we're a series, so extract with view to that.
            # Grab the season from the title.
            title = soup.find('h1').text
            season = self.util.find_numeric(title)
            # First entry is first episode - no link.
            self._extract_iframe(
                soup,
                ScraperBase.MEDIA_TYPE_TV,
                season=season,
                episode=1
            )
            for link, episode_soup in other_links:
                episode = self.util.find_numeric(link.text)
                self._extract_iframe(
                    episode_soup,
                    ScraperBase.MEDIA_TYPE_TV,
                    season=season,
                    episode=episode
                )
        else:
            # we're probably a movie, just extract
            self._extract_iframe(soup, ScraperBase.MEDIA_TYPE_FILM)

    def _extract_iframe(self, soup, asset_type, season=None, episode=None):
        title = soup.find('h1').text
        for iframe in soup.select('div.filmicerik iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=iframe['src'],
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode,
                                     asset_type=asset_type
                                     )

