# coding=utf-8

from sandcrawler.scraper import ScraperBase, ScraperFetchException, SimpleScraperBase


class ArmagedomFilmesBiz(SimpleScraperBase):
    BASE_URL = 'http://www.armagedomfilmes.biz'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)
        raise NotImplementedError('Domain is blocked. O domínio está indisponível por ordem da 1ª Vara da Justiça Federal da subseção de Sorocaba.')
        self.search_term_language = "por"

        self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(
            ScraperBase.URL_TYPE_SEARCH,
            self.BASE_URL)

        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    def _fetch_next_button(self, soup):
        next = soup.find('a', text='»')
        self.log.debug('---------------')
        return next['href'] if next else None

    def _fetch_no_results_text(self):
        # return u'Desculpe a palavra ou página que procura não consta em nossa base de dados.'
        return u'não gerou resultados'

    def _parse_search_result_page(self, soup):
        for result in soup.select('a.thumb'):
            # Only grab links that start with "Assistir" - translates to "Watch";
            # Others are informative blog posts.
            # eg "Watch - Sons of Anarchy Online"

            if result['title'].startswith('Assistir'):
                self.submit_search_result(
                    link_url=result['href'],
                    link_title=result['title']
                )

    def _parse_series_page(self, soup):
        title = soup.title.text
        results = soup.select('ul.bp-series a')
        for result in results:
            self.submit_search_result(
                link_title=title + " " + result.text,
                link_url=result.get('href')
            )
        return len(results) > 0

    def parse(self, parse_url, **extra):
        for soup in self.soup_each([parse_url, ]):
            self._parse_parse_page(soup)

    def _parse_seriadosonline(self, url, title, season, episode):
        soup = self.get_soup(url)
        for iframe in soup.select('iframe'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=iframe['src'],
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode,
                                     )
        for lnk in soup.select('a#videott') + soup.select('.botaoAbrir'):
            self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                     link_url=lnk.href,
                                     link_title=title,
                                     series_season=season,
                                     series_episode=episode,
                                     )

    def _parse_parse_page(self, soup):
        # Find every link under 'address' that starts with "Assistir" -
        # translates to "Watch";
        # eg "Watch - Episode 1"
        series_block = ''
        try:
            series_block = soup.find('div', 'lista-plyers servers niceScroll')
        except:
            pass
        if series_block:
            for season in soup.find('div', 'lista-plyers servers niceScroll').find_all('div'):
                season_text = ''
                try:
                    season_text = season.find('b').text
                except:
                    pass
                if season_text:
                    episodes = season.find_all('address')
                    for ep in episodes:
                        try:
                            episode_text = ep.find('a').text
                        except:
                            pass
                        if not episode_text.startswith('Assistir'):
                           continue
                        series_episode = self.util.find_numeric(''.join(episode_text))
                        series_season = self.util.find_numeric(''.join(season_text))
                        episode_url = ''
                        try:
                            episode_url =  ep.find('a')['href']
                        except:
                            pass
                        if episode_url:
                            if 'seriadosonline.biz' in episode_url:
                                # This is a sister site that has most of the tv.
                                self._parse_seriadosonline(
                                    episode_url,
                                    ep.find('a').text,
                                    series_season,
                                    series_episode,
                                )
                            else:
                                self.submit_parse_result(
                                    link_url=episode_url,
                                    link_title=episode_text,
                                    series_season=series_season,
                                    series_episode=series_episode,
                                )


        # Movie pages (and possibly some tv?) have iframes too.
        # Each iframe embeds another iframe, which is what we want.

        for iframe in soup.select('.link-video'):
            source = iframe['data-src']
            if not source or 'banner' in source or source.endswith('.gif'):
                continue
            # Skip youtube.
            if source.startswith('https://www.youtube.com') or source.startswith('//www.youtube.com') or\
                source.startswith('http://www.youtube'):
                continue
            self.submit_parse_result(
                index_page_title=soup.title.text.strip(),
                link_url=source,
                link_title=soup.find('h1', 'tt left').text,
            )

            # #LEGACY CODE BELOW
            # try:
            #     iframe_soup = self.get_soup(source)
            # except ScraperFetchException:
            #     self.log.exception('Failed to fetch %s', source)
            #     continue
            # for sub_iframe in iframe_soup.select('iframe'):
            #     # Skip local ones (ads!)
            #     subsource = sub_iframe.get('src', sub_iframe.get('data-src', None))
            #     if not subsource.startswith(
            #             'http://armagedomfilmes.biz') and \
            #             not subsource.startswith(
            #                 'http://www.armagedomfilmes.biz'):
            #         self.submit_parse_result(
            #             link_url=subsource
            #         )
