#coding=utf-8

import re

from sandcrawler.scraper import ScraperBase, ScraperParseException, ScraperFetchException


class CwerWS(ScraperBase):

    BASE_URL = 'http://cwer.ru'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "rus"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def search(self, search_term, media_type, **extra):
        search_url = self.BASE_URL + '/sphinx/?s=' + self.util.quote(
            search_term)
        for soup in self.soup_each([search_url, ]):
            self._parse_search_results(soup)
            # Then grab all the extra pages here and iterate through.
            for page_link in soup.select('div.paginator a'):
                if not self.can_fetch_next():
                    break
                self._parse_search_results(
                    self.get_soup(self.BASE_URL + page_link['href'])
                )

    def _parse_search_results(self, soup):
        if unicode(soup).find(
            u'Новостей не обнаружено') >= 0:
            return self.submit_search_no_results()
        for title in soup.select('div.nodetitle'):
            # Grab only links starting with node - others are categories.
            # XXX Perhaps check the 'category' to stop us getting a whole
            # bunch of books and apps.
            link = title.find('a', href=re.compile('^/node'))
            if link:
                self.submit_search_result(
                    link_url=self.BASE_URL + link['href'],
                    link_title=link.text
                )


    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_parse_page(self, soup):
        for hidden_tag in soup.select('div.tag_hide script'):
            # Simple obfuscation - does a document.write(HTML)
            # Extract that out, soup it, find our linkss
            match = re.match(
                '.*document\.write\((.*)\);.*',
                hidden_tag.text
            )
            if match:
                html = match.group(1)
                hidden_soup = self.make_soup(html)
                for link in hidden_soup.select('a'):
                    if link['href'].startswith('/lnk/'):
                        try:
                            response = self.get(self.BASE_URL + link['href'])
                        except ScraperFetchException:
                            self.log.error('Could not follow link: %s', link)
                        else:
                            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                     link_url=response.url,
                                                     link_title=link.text,
                                                     )
                    else:
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=link['href'],
                                                 link_title=link.text,
                                                 )
            else:
                raise ScraperParseException('Failed to extract hidden tags.')


