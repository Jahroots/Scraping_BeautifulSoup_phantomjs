#coding:utf-8

from scraper import ScraperBase


class SecurityLinksCom(ScraperBase):
    def setup(self):
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://security-links.com')

    @staticmethod
    def _parse_links(soup):
        links = soup.select('#mess a')
        links = [link['href'].strip() for link in links]
        return links

    def expand(self, url, **extra):
        soup = self.get_soup(url)

        if u'le lien est protegé par un mot de passe' in soup.text:
            if 'password' in extra:
                soup = self.post_soup(url, data=dict(passe=extra.get('password'), submit='Valider'))
                if u'Le mot de passe est incorrect' in soup.text:
                    self.log.error("Incorrect link password")
                    return []
            else:
                self.log.warning("Encountered link with password but no password available")

        return self._parse_links(soup)

