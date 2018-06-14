# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class FilmovizijaWs(SimpleScraperBase):
    BASE_URL = 'http://www.filmovizija.live'
    OTHERS_URLS = ['http://www.filmovizija.tv', 'http://www.filmovizija.ws']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'eng'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    TRELLO_ID = 'x89sMZYf'


    def get(self, url, **kwargs):
        return super(FilmovizijaWs, self).get(url, allowed_errors_codes=[403, 400, ], **kwargs)

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/search.php?all=all&keywords={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"Your search didn't return any result"

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'next »')
        return self.BASE_URL+'/'+next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found = 0
        collected = set()
        for results in soup.select('ul.cbp-rfgrid li > a'):
            title = results.text
            get_id = ''
            try:
                get_id = results['id']
            except KeyError:
                pass
            if results['href'] in collected:
                continue
            collected.add(results['href'])
            if 'loepi' in get_id:
                series_soup = self.get_soup(results['href'])
                for ep_link in series_soup.select('div.epi a.toolt'):
                    ep_link = self.BASE_URL + '/episode.php?vid=' + ep_link['data-url'].split('uniq=')[-1]
                    if ep_link not in collected:
                        collected.add(ep_link)
                        self.submit_search_result(
                            link_url=ep_link,
                            link_title=title,
                        )
            else:
                self.submit_search_result(
                    link_url=results['href'],
                    link_title=title,
                )
            found = 1
        if not found:
            return self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        ids_text = soup.select('div#upper a')
        if ids_text:
            title = None
            try:
                title = soup.select_one('div.heading_rest_v').text
            except AttributeError:
                title = soup.select_one('div.heading_rest').text
            for id_text in ids_text:
                id_text = id_text['id']
                data = {'id': id_text}
                movie_soup= self.post_soup('http://www.filmovizija.ws/morgan.php', data=data)
                movie_link = movie_soup.select_one('p')
                if movie_link:
                    movie_link = movie_link.text
                    self.submit_parse_result(
                        link_url=movie_link,
                        index_page_title=index_page_title,
                        link_title=title
                    )
        else:
            try:
                title = soup.select_one('div.heading_rest_v').text
            except AttributeError:
                title = soup.select_one('div.heading_rest').text
            movie_links = soup.select('tr#linktr span.fullm a')
            season, episode = self.util.extract_season_episode(title)
            for movie_link in movie_links:
                movie_link = movie_link['href']
                self.submit_parse_result(
                    link_url=movie_link,
                    index_page_title=index_page_title,
                    series_season=season,
                    series_episode=episode,
                    link_title=title
                )
            for online_link in soup.select('ul.tabs a.direct'):
                movie_link = online_link['id']
                self.submit_parse_result(
                    link_url=movie_link,
                    index_page_title=index_page_title,
                    series_season=season,
                    series_episode=episode,
                    link_title=title
                )
