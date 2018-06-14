#coding=utf-8
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase

class WatchSeriesAg(SimpleScraperBase):
    BASE_URL = 'https://seriesfree.to'
    OTHERS_URLS = ['http://watch-series.ag']

    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    SINGLE_RESULTS_PAGE = True
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    USER_AGENT_MOBILE = False

    def _fetch_no_results_text(self):
        return u'We are sorry there are no links.'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/suggest.php?ajax=1&s={}&type=TVShows'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        if soup.find('a', text=u' › ') and soup.find('a', text=u' › ')['href'] :
            href = soup.find('a', text=u' › ')['href']
            if not href.startswith('http'):
                href = self.BASE_URL + href
            return href
        else:
            return None

    def _parse_search_result_page(self, soup):
        links = soup.select('li a')

        if not links or len(links) == 0:
            return self.submit_search_no_results()
        for link in links:
            url = link.href
            if url.startswith('/'):
                url = self.BASE_URL + url
            try:
                episode_soup = self.get_soup(url)
            except Exception as e:
                continue
            episodes_list = episode_soup.select('ul[class*="simple-list"] li[itemprop="episode"]')

            for episode in episodes_list:
                # Short circuit 0 links results.
                epnum = episode.select_one('span.epnum')
                if epnum and epnum.text.find('(0 links)') > -1:
                    self.log.debug('Skipping 0 links reference.')
                    continue

                episode_link = episode.select_one('a[itemprop="url"]')
                if episode_link:
                    link = episode_link['href']
                    if link.startswith('/'):
                        link = self.BASE_URL + link
                    self.submit_search_result(
                        link_url=link,
                        link_title=episode.text,
                    )

    def _parse_parse_page(self, soup):
        title = soup.find('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        season, episode = self.util.extract_season_episode(title)
        episodes_table = soup.select('div.links a[class="watch-btn btn btn-success btn-3d"]')

        if episodes_table:
            for episode_table in episodes_table:
                link_id = self.BASE_URL + episode_table['href']
                soup = self.get_soup(link_id)

                link = soup.select_one('a[class="action-btn txt-ell W btn btn-success btn-3d"]')
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    series_season=season,
                    series_episode=episode,
                    link_url= link.href
                )
