# coding=utf-8
import re
from sandcrawler.scraper import OpenSearchMixin, ScraperBase, SimpleScraperBase

class Filmi7Com(OpenSearchMixin, SimpleScraperBase):
    BASE_URL = 'http://filmi7.com'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'bul'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    USER_AGENT_MOBILE = False

    def get(self, url, **kwargs):
        return super(Filmi7Com, self).get(url, allowed_errors_codes=[403, ], **kwargs)

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', name=u'nextlink')
        return next_link['href'] if next_link else None

    def _fetch_no_results_text(self):
        return u'Unfortunately, site search yielded no results. Try to change or shorten your request.'

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.new_movie12'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('div.description-title')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        rels = re.findall('rel:"(.*)"}', unicode(soup))
        for rel in rels:
            data_id = {'rel': rel}
            iframe_link = self.post_soup('http://filmi7.com/engine/ajax/dci.php', data=data_id).select_one('iframe')['src']
            self.log.warning(iframe_link)
            if 'http' not in iframe_link:
                continue
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe_link.encode('ascii', 'ignore').decode('ascii'),
                link_title=iframe_link,
                series_season=series_season,
                series_episode=series_episode,
            )
        rels = re.findall("""sk\.init\(\'(.*)\',""", soup.text)
        for rel in rels:
            data={'rel':rel}
            link = self.post('http://filmi7.com/engine/ajax/dci.php?get=film', data=data).text
            if link:
                if 'http' not in link:
                    continue
                self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=link.encode('ascii', 'ignore').decode('ascii'),
                        link_title=link,
                        series_season=series_season,
                        series_episode=series_episode,
                    )
            else:
                self.log.warning('No link found for rel %s on %s',
                    rel, soup._url)
        on_player = soup.select_one('div#onplay-player iframe')
        if on_player:
            on_player_link = on_player['src']
            if 'http' in on_player_link:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=on_player_link.encode('ascii', 'ignore').decode('ascii'),
                    link_title=on_player.text,
                    series_season=series_season,
                    series_episode=series_episode,
                )
