# coding=utf-8

import re

from sandcrawler.scraper import ScraperBase
from sandcrawler.scraper import SimpleGoogleScraperBase, ScraperException


class InterCambiosVirtualesOrg(SimpleGoogleScraperBase, ScraperException):
    # Note - this by default doesn't use "Google" but uses a partner
    # affiliate that uses the API.  Gives exactly the same results, so, win.

    BASE_URL = 'http://www.intercambiosvirtuales.org'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        self.search_term_language = "spa"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(
            ScraperBase.URL_TYPE_LISTING,
            self.BASE_URL)

    def _fetch_no_results_text(self):
        return 'did not match any documents'

    def _parse_search_result_page(self, soup):
        found=0
        for result in soup.select('h3.r a'):
            # Follow it so we get the URL.
            href = result['href']
            if href.startswith('/url'):
                try:
                    followed_response = self.get(
                        'https://www.google.com' + result['href'],
                        headers={
                            'User-Agent': self.USER_AGENT,
                        }
                    )
                    href = followed_response.url
                except ScraperException as error:
                    self.log.error("Scraper Error: %s", error)
                    continue
            self._handle_search_result(href, result.text)
            found=1
        if not found:
            return self.submit_search_no_results()

    def _handle_search_result(self, response, link_title):
        # Skip tag pages.
        url = response  # .url
        if re.match('^' + self.BASE_URL + '/tag/', url):
            return
        self.submit_search_result(
            link_url=url,
        )

    def parse(self, parse_url, **extra):
        # This site has some... weirdness going on, or BS does.
        # It's causing BS to stop 1/3 of the way thtrough the page,
        # just after the first <legend>
        # So we'll get the links out using a regex :(
        # All the links are http://re-direcciona.me, so it's a touch less blah.
        # Use the soup we can get to extract a title, at least.
        content_soup = self.make_soup(self.get(parse_url).content)

        title = self.get_soup(parse_url).title.text.strip()
        page_title = episode = season = None
        page_title = content_soup.select('div#postheader h1 a')[0].text
        season, episode = self.util.extract_season_episode(page_title)
        content = content_soup.select('div[align="center"] span[style="font-family:trebuchet ms;"]')
        for content_block in content:
            ivpaste_links = None
            try:
                ivpaste_links = content_block.find_all('a')
            except AttributeError:
                pass
            for ivpaste_link in ivpaste_links:
                ivpaste_link = ivpaste_link['href']
                if '.png' in ivpaste_link:
                    continue
                redirect_link_soup = self.get_soup(ivpaste_link)
                redirect_link = redirect_link_soup.select_one('div#oculto a')['href']
                link_soup = self.get_soup(redirect_link)
                link = link_soup.select_one('iframe')
                if link:
                    movie_link = link['src']
                    self.submit_parse_result(index_page_title=title,
                                             link_url=movie_link,
                                             link_title=page_title,
                                             series_season=season,
                                             series_episode=episode,
                                             )
                else:
                    link = link_soup.select('script')[-1]
                    for movie_link in self.util.find_urls_in_text(link.text):
                        movie_link = movie_link.replace('(archive)', '')
                        self.submit_parse_result(index_page_title=title,
                                             link_url=movie_link,
                                             link_title=page_title,
                                             series_season=season,
                                             series_episode=episode,
                                             )

        # for link in re.findall('http://re-direcciona.me[^\"]*', content):
        #     if page_title is None:
        #         soup = self.make_soup(content)
        #         page_title = soup.select('div#postheader h1 a')[0].text
        #         season, episode = self.util.extract_season_episode(
        #             page_title)
        #     # Now follow the link to our actual endpoint
        #
        #     try:
        #         the_link = self.get(
        #             self.get(link).content.split('http-equiv="refresh" content="5; URL=')[1].split('">')[0]
        #         ).content.split('window.location="')[1].split('";</script>')[0]
        #
        #     except:
        #         the_link = \
        #             self.get(self.get(link).content.split('http-equiv="refresh" content="5; URL=')[1].split('">')[0]
        #                      ).content.split('iframe src="')[1].split('"></iframe>')[0]
        #         # self.log.warning(the_link)

            # if 'magnet' not in the_link :
            #     self.submit_parse_result(index_page_title=title,
            #                          link_url=the_link,
            #                          link_title=page_title,
            #                          series_season=season,
            #                          series_episode=episode,
            #                          )
