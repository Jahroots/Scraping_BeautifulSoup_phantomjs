# -*- coding: utf-8 -*-
from sandcrawler.scraper import ScraperBase, SimpleScraperBase, CloudFlareDDOSProtectionMixin


class _300mbunited(CloudFlareDDOSProtectionMixin, SimpleScraperBase):
    BASE_URL = 'http://www.300mbunited.me'
    OTHER_URLS = []

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = 'eng'

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

        self.requires_webdriver = True
        self.webdriver_type = 'phantomjs'

    def _fetch_no_results_text(self):
        return 'No posts found'

    def _fetch_next_button(self, soup):
        link = soup.select_one('.left')
        return link.parent['href'] if link else None

    def _parse_search_result_page(self, soup):
        found = 0
        for result in soup.select('h2.entry-title a'):
            self.submit_search_result(
                link_url=result['href'],
                link_title=result['title']
            )
            found = 1
        if not found:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):
        title = soup.select_one('h1').text.strip()
        season, episode = self.util.extract_season_episode(title)

        page_text = soup.select_one('div.post').text
        for link in self.util.find_urls_in_text(page_text):
            if link.startswith(self.BASE_URL):
                continue
            self.submit_parse_result(
                index_page_title=self.util.get_page_title(soup),
                link_url=link,
                link_title=title,
                series_season=season,
                series_episode=episode
            )


        found = 0
        link = soup.select_one('.p-con blockquote p a')
        if link:
            self.submit_parse_result(
                index_page_title=soup.title.text.strip(),
                link_url=link.href,
                link_passw='300mbunited',
                rar_passw='ultrascorp',
                link_title=title,
                series_season=season,
                series_episode=episode
            )
            found = 1

        if found:
            return

        # another page type
        link_passw = ''
        rar_passw = 'ultrascorp'
        for block in soup.select('.p-con blockquote p span'):
            if 'http' in block.text:
                link = block.text
            elif 'Link Password' in block.parent.text and not link_passw:
                link_passw = block.text
            elif 'RAR Password' in block.parent.text and link_passw:
                rar_passw = block.text

        if link_passw:
            self.submit_parse_result(
                index_page_title=soup.title.text.strip(),
                link_url=link,
                link_passw=link_passw,
                rar_passw=rar_passw,
                link_title=title,
                series_season=season,
                series_episode=episode
            )


