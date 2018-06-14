# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleScraperBase


class FilmLinks4UTo(SimpleScraperBase):
    BASE_URL = 'https://www.filmlinks4u.is'
    OTHER_URLS = ['http://www.filmlinks4u.to', 'http://www.filmlinks4u.is']

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "eng"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '?s=' + self.util.quote(search_term)

    def _fetch_no_results_text(self):
        return 'but nothing matched your search criteria'

    def _fetch_next_button(self, soup):
        link = soup.select_one('span#tie-next-page a')
        if link:
            return link['href']
        return None

    def _parse_search_result_page(self, soup):
        for result in soup.select('div.post-listing article'):
            link = result.select_one('h2.post-box-title a')
            if not link:
                continue
            self.submit_search_result(
                link_url=link['href'],
                link_title=link.text,
                image=self.util.find_image_src_or_none(result,
                                                'div.post-thumbnail img')
            )

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        for iframe in soup.select('div#movie_player iframe'):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=iframe['src'],
            )
        for external_link in soup.findAll(
                'a',
                text=re.compile('^Watch Online.*')):
            self.submit_parse_result(
                index_page_title=index_page_title,
                link_url=external_link['href'],
                link_title=external_link.text
                )

        # Find a post id in javascript
        postidsearch = re.search("'post_id':'(\d+)'", str(soup))
        if postidsearch:
            post_id = postidsearch.group(1)
            data={
                'action': 'create_player_box',
                'post_id': post_id
            }
            embed_soup = self.post_soup(
                self.BASE_URL + '/wp-admin/admin-ajax.php',
                data=data,
            )
            for tab in embed_soup.select('div.tab'):
                src = tab.get('data-href', None)
                if src:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=src,
                        link_title=tab.text,
                    )
            for iframe in embed_soup.select('iframe'):
                src = iframe.get('src', iframe.get('data-src'))
                if src:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=src
                    )




class SeriesPormegaCom(FilmLinks4UTo):
    BASE_URL = 'http://seriespormega.com'

    def setup(self):
        raise NotImplementedError('Deprecated, website no longer avilable')

    def _fetch_no_results_text(self):
        return 'Nothing Found'

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1 span[itemprop="name"]').text.strip()
        season, episode = self.util.extract_season_episode(title)

        for link in soup.select('div.entry a'):
            if 'pastespormega' in link.href:
                link = urllib.unquote(link.href.split('?s=')[-1])
                files_urls = self.get_soup(link)
                for file_url in files_urls.select('center a'):
                    urls = self.util.find_urls_in_text(file_url.text)
                    for url in urls:
                        self.submit_parse_result(
                            index_page_title=self.util.get_page_title(soup),
                            link_url=url,
                            link_title=file_url.text,
                            series_season=season,
                            series_episode=episode
                        )
                if 'pastespormega' not in link.href or 'http' in link.text:
                    url = link.href
                    self.submit_parse_result(
                        index_page_title=self.util.get_page_title(soup),
                        link_url=url.href,
                        link_title=link.text,
                        series_season=season,
                        series_episode=episode
                    )


