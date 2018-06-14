# coding=utf-8
import re
from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import AntiCaptchaMixin, SimpleScraperBase, CachedCookieSessionsMixin
from sandcrawler.scraper.caching import cacheable


class FilmeserialeonlineOrg(AntiCaptchaMixin, SimpleScraperBase, CachedCookieSessionsMixin):
    BASE_URL = 'http://www.filmeserialeonline.org'
    RECAPKEY = '6LcLBhQUAAAAACtt-2FptlfshI9rRZakENgwiK_H'
    TRELLO_ID = 'L8B5j4cF'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rom"

        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def get(self, url, **kwargs):
        return super(self.__class__, self).get(url, allowed_errors_codes=[404], **kwargs)

    def _fetch_no_results_text(self):
        return u'Nu am gasit ce cautai'

    def _fetch_search_url(self, search_term, media_type=None, start=1):
        self.start = start
        self.search_term = search_term
        return self.BASE_URL + '/page/{}/?s={}'.format(start, search_term)

    def _parse_search_results(self, soup):
        rslts = soup.select('div.peliculas div.item a')
        if not rslts:
            return self.submit_search_no_results()
        self._parse_search_result_page(soup)
        self.start += 1
        next_button_link = self._fetch_search_url(self.search_term, start=self.start)
        if next_button_link and self.can_fetch_next():
            self._parse_search_results(
                self.get_soup(
                    next_button_link
                )
            )

    def _parse_search_result_page(self, soup):
        found = 0
        rslts = soup.select('div.box div.box_item div.peliculas div.item > a')
        for result in rslts:
            link = result['href']
            if '/seriale/' in link:
                for episode in self.get_soup(link).select('div#seasons ul.episodios div.episodiotitle > a'):
                    self.submit_search_result(
                        link_url=episode['href'],
                        link_title=episode.text
                    )
            else:
                self.submit_search_result(
                    link_url=link,
                    link_title=result.find_next('h2').text,
                )
            found=1
        if not found:
            return self.submit_search_no_results()

    @cacheable()
    def _extract_parse_results(self, vid_id, parse_url):
        """
        Extracts the video - it can come from one of two different urls (but
         same functionality...)
         so just try to get it from both.
        """

        headers = {'Referer': parse_url}
        data = {'id': vid_id}

        soup1 = self.post_soup(
            # 'http://www.filmeserialeonline.org/wp-content/themes/grifus/includes/single/second.php',
            'http://www.filmeserialeonline.org/wp-content/themes/grifus/loop/second.php',
            data=data,
            headers=headers
        )
        soup2 = self.post_soup(
            'http://www.filmeserialeonline.org/wp-content/themes/grifus/includes/single/second.php',
            #'http://www.filmeserialeonline.org/wp-content/themes/grifus/loop/second.php',
            data=data,
            headers=headers
        )


        # If we find a recap, re-submit back to main page, then ttry again.
        if soup1.select('div.g-recaptcha') or soup2.select('div.g-recaptcha'):
            self.post_soup(
                'http://www.filmeserialeonline.org/wp-content/themes/grifus/includes/single/second.php',
                data={
                    'call': self.get_recaptcha_token()
                },
                headers=headers
            )

            soup1 = self.post_soup(
                'http://www.filmeserialeonline.org/wp-content/themes/grifus/loop/second.php',
                data=data,
                headers=headers
            )
            soup2 = self.post_soup(
                'http://www.filmeserialeonline.org/wp-content/themes/grifus/includes/single/second.php',
                data=data,
                headers=headers
            )
            self.save_session_cookies()




        results = []
        for iframe in soup1.select('iframe'):
            results.append(iframe['src'])
        for iframe in soup2.select('iframe'):
            results.append(iframe['src'])
        return results

    def _parse_parse_page(self, soup):

        index_page_title = self.util.get_page_title(soup)
        title_block = soup.select_one('h1')
        title = title_block and title_block.text or ''
        id_res = re.search("id\: (\d+)", soup.text)

        if id_res:
            id_result = id_res.group(0).split(':')[1].strip()
            for result in self._extract_parse_results(id_result, soup._url):
                self.submit_parse_result(
                    index_page_title=index_page_title,
                    link_title=title,
                    link_url=result
                )


