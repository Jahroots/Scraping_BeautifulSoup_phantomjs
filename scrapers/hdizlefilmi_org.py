# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase
import re

class HdizlefilmiOrg(SimpleScraperBase):
    BASE_URL = 'http://www.hdizlefilmi.org'
    OTHER_URLS = []
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    MEDIA_TYPES = [ ScraperBase.MEDIA_TYPE_FILM, ]
    SINGLE_RESULTS_PAGE = True

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    def _fetch_search_url(self, search_term, media_type):
        return '{base_url}/?&s={search_term}'.format(base_url=self.BASE_URL, search_term=search_term)

    def _fetch_no_results_text(self):
        return u'Üzgünüz, kriterlerinize uygun film yok'

    def _fetch_next_button(self, soup):
        next_button = soup.find('a', text='>')
        if next_button:
            return next_button.href
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.moviefilm'):
            link = result.select_one('a')
            self.submit_search_result(
                link_url=link.href,
                link_title=link.text,
                image=self.util.find_image_src_or_none(result, 'img'),
            )
    def _parse_parse_page(self, soup):
        for link in soup.select('div#pagelink a'):
            video_soup = self.get_soup(link.href)
            index_page_title = self.util.get_page_title(video_soup)
            title = soup.select_one('h1')
            if title and title.text:
                series_season, series_episode = self.util.extract_season_episode(title.text)
            for iframe in video_soup.select('div.video iframe'):
                if 'facebook' in iframe['src']:
                    continue
                url = iframe['src']

                if url.startswith('http://www.filmizlejet.org/'):

                    response = self.get(
                        url,
                        headers={'Referer': link.href}
                        )

                    urls = list(self.util.find_file_in_js(response.content))
                    if urls:
                        url = 'http://www.filmizlejet.org/' + urls[0]

                        response = self.get(
                            url,
                            headers={'Referer': iframe['src']},
                            allow_redirects=False
                        )
                        if response.is_redirect:
                            url = response.headers.get('Location')
                        else:
                            self.log.warning('Failed to follow url in %s -> %s', link.href, iframe['src'])
                            continue
                    else:
                        self.log.warning('Could not find url in %s -> %s', link.href, iframe['src'])
                        continue

                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url,

                )
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)
        for result_link in soup.select('div.keremiya_part a'):
            if '#respond' in result_link.href:
                continue
            film_soup = self.get_soup(result_link.href)
            for link in film_soup.select('div#kendisi iframe'):
                link_url = link['src']
                link_title = link.text
                if 'youtube' in link_url or 'simdiarabul' in link_url or 'simdifilmizle' in link_url:
                    continue
                if 'http' not in link_url:
                    link_url = 'http:' + link_url
                self.submit_parse_result(
                    index_page_title=self.util.get_page_title(soup),
                    link_url=link_url,
                    link_title=link_title,
                    series_season=series_season,
                    series_episode=series_episode,
                )
