# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class DpseriesNet(SimpleScraperBase):
    BASE_URL = 'http://dpseries.info'
    OTHER_URLS = ['http://dpseries.net']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = ''
        try:
            link = soup.find('a', text=u'» suivante')
        except AttributeError:
            pass
        self.log.debug('------------------------')
        if link:
            return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        any_results = False
        for results in soup.select('div.movief a'):
            result = results['href']
            title = results.text.strip()
            self.submit_search_result(
                link_url=result,
                link_title=title
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        season = title.split('Saison ')[-1].strip()
        episode = soup.find('div', 'keremiya_part').find_all('span')[-1].text.strip()
        select_links = soup.find('select', attrs={'name':"select_items"}).find_all('option')[1:]

        iframe_l = soup.find('iframe', id='film_main')['src']

        self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                 link_url=iframe_l,
                                 link_title=title,
                                 series_season=season,
                                 series_episode=episode,
                                 )



        for select_link in select_links:
            select_movie_link = select_link['value']
            self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                     link_url=select_movie_link,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode,
                                     )

        for ep in soup.select('div.keremiya_part a'):
            ep_soup = self.get_soup(ep['href'])
            title = ep_soup.select_one('h1').text.strip()
            season = title.split('Saison ')[-1].strip()
            episode = ep_soup.find('div', 'keremiya_part').find_all('span')[-1].text.strip()
            select_links = ep_soup.find('select', attrs={'name': "select_items"}).find_all('option')[1:]
            for select_link in select_links:
                select_movie_link = select_link['value']

                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=select_movie_link,
                                         link_title=title,
                                         series_season=season,
                                         series_episode=episode,
                                         )