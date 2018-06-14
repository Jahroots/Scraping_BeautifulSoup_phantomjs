# coding=utf-8

from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class FilmStreamingVfCom(SimpleScraperBase):
    BASE_URL = 'http://regarder.film-streaming-vf.com'
    OTHER_URLS = ['http://film-streaming-vf.in', 'http://film-streaming-vf.co', 'http://film-streaming-vf.live', 'http://voir.film-streaming-vf.com', 'http://film-streaming-vf.pw', 'http://film-streaming-vf.pro', 'http://film-streaming-vf.xyz', 'http://film-streaming-vf.life', 'http://film-streaming-vf.ws', 'http://film-streaming-vf.me', 'http://film-streaming-vf.cc', 'http://filmstreamingvf.life', 'http://film-streaming-vf.tv', 'http://filmstreamingvf.life',
                  'http://filmstreamingvf.me', 'http://filmstreamingvf.ws', 'http://film-streaming-vf.bz',
                  'http://film-streaming-vf.org', 'http://filmsstreaming-vf.com']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]
    TRELLO_ID = 'IFIOJBma'

    def _fetch_search_url(self, search_term, media_type):
        return self.BASE_URL + '/?s={}'.format(self.util.quote(search_term))

    def _fetch_no_results_text(self):
        return u"Désolé, le film n'a pas été trouvé"

    def _fetch_next_button(self, soup):
        next_link = soup.find('a', text=u'»')
        return next_link['href'] if next_link else None

    def _parse_search_result_page(self, soup):
        found=0
        for results in soup.select('div.filmcontent div.moviefilm a'):
            image = self.util.find_image_src_or_none(results, 'img')
            result = results['href']
            title = results.text
            self.submit_search_result(
                link_url=result,
                link_title=title,
                image = image
            )
            found=1
        if not found:
            return self.submit_search_no_results()


    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        index_page_title = self.util.get_page_title(soup)
        for ep_link in soup.select('div.keremiya_part a'):
            if 'http' not in ep_link['href']:
                continue
            movie_soup = self.get_soup(ep_link['href'])
            for movie_link in movie_soup.select('div.filmicerik iframe'):
                if 'toro-tags' in movie_link['src'] or 'iisksudks' in movie_link['src']:
                    continue
                if movie_link['src']:
                    self.submit_parse_result(
                        index_page_title=index_page_title,
                        link_url=movie_link['src'],
                        link_text=title,
                    )
        for movie_link in soup.select('div.filmicerik iframe'):
            if 'toro-tags' in movie_link['src'] or 'iisksudks' in movie_link['src']:
                continue
            if movie_link['src']:
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=movie_link['src'],
                    link_text=title,
                )


class FilmstreamVkCom(FilmStreamingVfCom, SimpleScraperBase):
    BASE_URL = 'http://filmstreamvk.me'
    OTHER_URLS = ['http://filmstreamvk.co', 'http://filmstreamvk.org', 'http://filmstreamvk.biz', 'http://filmstreamvk.ws', 'http://filmstreamvk.com', 'http://filmstreamvk.net']
    SCRAPER_TYPES = [ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'fra'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV]
    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING]