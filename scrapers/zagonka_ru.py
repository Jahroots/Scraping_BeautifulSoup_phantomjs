
# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase, SimpleScraperBase


class ZagonkaRu(SimpleScraperBase):
    BASE_URL = 'https://zagonka.ru'
    OTHER_URLS = ['http://zagonka.ru']
    SCRAPER_TYPES = [ ScraperBase.SCRAPER_TYPE_OSP, ]
    LANGUAGE = 'rus'
    LONG_SEARCH_RESULT_KEYWORD = '2017'
    MEDIA_TYPES = [ScraperBase.MEDIA_TYPE_FILM, ScraperBase.MEDIA_TYPE_TV, ]

    URL_TYPES = [ScraperBase.URL_TYPE_SEARCH, ScraperBase.URL_TYPE_LISTING, ]

    USER_AGENT_MOBILE = False
    SINGLE_RESULTS_PAGE = True  # Pagination broken
    SEARCH_TERM = ''

    def _fetch_next_button(self, soup):
        return None

    def _fetch_no_results_text(self):
        return u'К сожалению, поиск по сайту не дал никаких результатов'

    def _fetch_search_url(self, search_term, media_type ):
        self.SEARCH_TERM = search_term
        return self.BASE_URL + '/poisk={}/'.format(search_term)

    def search(self, search_term, media_type, **extra):
        soup = self.post_soup(self.BASE_URL + '/engine/ajax/search.php', data={'query': search_term})
        if u'Ничего не найдено. Пожалуйста, попробуйте изменить запрос' in unicode(soup):
            return self.submit_search_no_results()

        self._parse_search_result_page(soup)

    def _parse_search_result_page(self, soup):

        for result in soup.select('a'):
                self.submit_search_result(
                    link_url=result.href,
                    link_title=result.text,
                    image=self.util.find_image_src_or_none(result, 'img'),
                )

    def decode_uppod(self, file_code):
            file_code = file_code[1:]
            uni_file_code = ''
            for i in range(0, len(file_code), 3):
                uni_file_code += '%u0' + file_code[i:i + 3]
            decoded_url =re.sub(r'%u([a-fA-F0-9]{4}|[a-fA-F0-9]{2})', lambda m: chr(int(m.group(1), 16)), uni_file_code)
            return decoded_url

    def _parse_parse_page(self, soup):
        index_page_title = self.util.get_page_title(soup)
        series_season = series_episode = None
        title = soup.select_one('h1')
        if title and title.text:
            series_season, series_episode = self.util.extract_season_episode(title.text)

        result = None
        script_text = soup.find('script', text=re.compile(r'file:'))

        if script_text:
            script_text = script_text.text
            result = re.search("""file:\"(.*)\",""", script_text).group(1)

        else:
            script_text = soup.find('script', text=re.compile(r'pl:'))
            if script_text:
                script_text = script_text.text
                result = re.search("""pl:\"(.*)\",""", script_text).group(1)

        if result:
            url = self.decode_uppod(result)
            self.log.warning(url)
            if 'http' not in url:
                url = 'http:' + url

        else:
            script_text = soup.select_one('iframe')
            if script_text:
                url = script_text['src']
                self.log.warning(url)
                if 'http' not in url:
                    url = 'http:' + url
            else:
                url = None

        if url:
            self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_url=url,
                    link_title=url,
                    series_season=series_season,
                    series_episode=series_episode,
                )
