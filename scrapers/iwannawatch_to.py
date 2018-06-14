# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class IwannawatchTo(SimpleScraperBase):
    BASE_URL = 'https://www.iwannawatch.is'
    OTHER_URLS = ['http://www.iwannawatch.to']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, verify=False, allowed_errors_codes=[404], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u'Sorry, but nothing matched your search terms'

    def _fetch_next_button(self, soup):
        next = soup.find('a', text=u'>')
        self.log.debug('---------------')
        return next['href'] if next else None

    def _parse_search_result_page(self, soup):
        any_results = False
        for results in soup.select('h1.entry-title a'):
            result = results['href']
            title = results.text.strip()
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            any_results = True
        if not any_results:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        download_links= soup.select('div.entry-content a.external')
        for download_link in download_links:
            if 'cineview' in download_link['href']:
                movie_soup = self.get_soup(download_link['href'])
                movie_link = ''
                try:
                    movie_link = movie_soup.find('div', id='mrc_vi_play').find('iframe')['src']
                except AttributeError:
                    try:
                        movie_link = movie_soup.find('div', id='player').find('iframe')['src']
                    except (AttributeError, TypeError):
                        pass
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link,
                    link_text=title,
                )
            else:
                if 'example.com' not in download_link['href']:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=download_link['href'],
                        link_text=title,
                    )

        post_id = soup.text.split("post_id\':")[-1].split("}")[0].strip()
        post_id_data = {'action': 'create_player_box', 'post_id': post_id}
        players_id_soup = self.post_soup('http://www.iwannawatch.to/wp-admin/admin-ajax.php', data=post_id_data)
        for players_id in players_id_soup.select('div.tab')[:-2]:
            players_id = players_id['rel']
            if players_id:
                link_data = {'action':'get_embed', 'player_id':players_id, 'post_id':post_id}
                link_soup = self.post_soup('http://www.iwannawatch.to/wp-admin/admin-ajax.php', data=link_data)
                source_link = link_soup.find('iframe')['src']
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=source_link,
                    link_text=title,
                )
