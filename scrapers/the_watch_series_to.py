# coding=utf-8

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase
import base64


class TheWatchSeriesTo(SimpleScraperBase):
    BASE_URL = 'http://dwatchseries.to'
    OTHER_URLS = [
        'http://www.tvbuzer.com',
        'http://itswatchseries.to',
        'http://watchseriesonline.in',
        'http://watchseriesonline.eu',
        'http://xwatchseries.to',
        'http://ewatchseries.to',
        'http://mywatchseries.to',
        'http://onwatchseries.to',
        'http://thewatchseriestv.to/',
        'http://watchseriestv.to/',
        'http://watchseries.to/',
        'http://watch-series-tv.to/',
        'http://thewatchseries.to/',
        'http://thewatchseries.to',
    ]

    ALLOW_FETCH_EXCEPTIONS = True

    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def setup(self):
        super(TheWatchSeriesTo, self).setup()
        self._request_connect_timeout = 300
        self._request_response_timeout = 600


    #def get(self, url, **kwargs):
    #    return super(TheWatchSeriesTo, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _fetch_no_results_text(self):
        return u'We are sorry there are no links.'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search/{}'.format(self.util.quote(search_term))

    def _fetch_next_button(self, soup):
        if soup.find('a', text=u'Next Page') and soup.find('a', text=u'Next Page')['href'] :
            href = soup.find('a', text=u'Next Page')['href']
            if not href.startswith('http'):
                href = self.BASE_URL + href
            return href
        else:
            return None

    def _parse_search_result_page(self, soup):
        links = soup.select('div.search-item-left a[target="_blank"]')

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
            episodes_list = episode_soup.select('li[itemprop="episode"]')

            for episode in episodes_list:
                # Short circuit 0 links results.
                epnum = episode.select_one('span.epnum')
                if epnum and epnum.text.find('(0 links)') > -1:
                    self.log.debug('Skipping 0 links reference.')
                    continue

                episode_link = episode.select_one('meta[itemprop="url"]')
                if episode_link:
                    link = episode_link['content']
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
        episodes_table = ''
        try:
            episodes_table = soup.find('table', id='myTable').find_all('a', 'buttonlink')
        except:
            pass
        if episodes_table:
            for episode_table in episodes_table:
                link_id = episode_table['href']
                self.log.debug(link_id)
                if 'ad.php' in link_id or \
                    'Sponsored' in link_id or \
                    '/watch-series-online.html' in link_id:
                    continue
                if link_id.startswith('/cale.html'):
                    link_text = link_id.split('?r=')[-1]
                    url = base64.decodestring(link_text)
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        series_season=season,
                        series_episode=episode,
                        link_url=url
                    )

                else:
                    url = link_id
                    url = base64.decodestring(url.split('r=')[1])
                    self.submit_parse_result(
                            index_page_title=index_page_title,
                            series_season=season,
                            series_episode=episode,
                            link_url=url
                    )



class WatchSeriesPh(TheWatchSeriesTo):
    BASE_URL = 'http://watchseries.ph'

class WatchSeriesAg(TheWatchSeriesTo):
    BASE_URL = 'https://seriesfree.to'
    OTHERS_URLS = ['http://watch-series.ag']

class The_Watch_SeriesTo(TheWatchSeriesTo):
    BASE_URL = 'http://dwatchseries.to'
    OTHER_URLS = ['http://the-watch-series.to']

    def setup(self):
        raise NotImplementedError('Deprecated, uses the_watch_series.to')

class WatchSeriesClub(TheWatchSeriesTo):
    BASE_URL = 'http://watchseriesfree.me'
    OTHERS_URLS = ['http://watchseries1.me', 'http://watchseries.club']



