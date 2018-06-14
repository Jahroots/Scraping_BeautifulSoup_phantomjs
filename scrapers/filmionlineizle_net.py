# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class FilmionlineizleNet(SimpleScraperBase):
    BASE_URL = 'http://www.filmionlineizle.net'
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'tur'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return None

    def _fetch_next_button(self, soup):
        link = ''
        try:
            link = soup.find('a', text=u'»')
        except AttributeError:
            pass
        self.log.debug('------------------------')
        if link:
            return link['href'] if link else None

    def _parse_search_result_page(self, soup):
        any_results = False
        for results in soup.select('div.moviefilm'):
            result = results.a['href']
            title = results.a.text.strip()
            self.submit_search_result(
                link_url=result,
                link_title=title,
                image=self.util.find_image_src_or_none(results, 'img')
            )
            any_results = True
        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        for ep in soup.select('div.keremiya_part a'):
            if 'http' not in ep['href']:
                continue
            ep_soup = self.get_soup(ep['href'])
            iframe_l = ''
            try:
                iframe_l = ep_soup.find('div','filmicerik').find('iframe')['src']
            except AttributeError:
                pass
            if self.BASE_URL in iframe_l:
                ep_soup = self.get_soup(iframe_l)
                movie_l = ''
                try:
                    movie_l = ep_soup.find('div', 'filmicerik').find('iframe')['src']
                except AttributeError:
                    pass
                if movie_l:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=movie_l,
                                             link_title=title,
                                             )

            else:
                if 'drive.google.com' in iframe_l:
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=iframe_l,
                                             link_title=title,
                                             )
                else:

                    if iframe_l and 'http' not in iframe_l:
                        iframe_l = 'https:'+iframe_l
                    self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=iframe_l,
                                             link_title=title,
                                             )
        iframe_l = ''
        try:
            iframe_l = soup.find('div','filmicerik').find('iframe')['src']
        except AttributeError:
            pass

        if self.BASE_URL in iframe_l:
            ep_soup = self.get_soup(iframe_l)
            movie_l = ''
            try:
                movie_l = ep_soup.find('div', 'filmicerik').find('iframe')['src']
            except AttributeError:
                pass
            if movie_l:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=movie_l,
                                         link_title=title,
                                         )
        else:
            if 'drive.google.com' in iframe_l:
                self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                         link_url=iframe_l,
                                         link_title=title,
                                         )
            else:
                if iframe_l and 'youtube' not in iframe_l:
                   self.submit_parse_result(index_page_title=self.util.get_page_title(soup),
                                             link_url=iframe_l,
                                             link_title=title,
                                             )