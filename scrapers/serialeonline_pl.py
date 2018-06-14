# -*- coding: utf-8 -*-

from sandcrawler.scraper.extras import AntiCaptchaImageMixin, ScraperBase
from sandcrawler.scraper import ScraperParseException
from sandcrawler.scraper import SimpleScraperBase
from sandcrawler.scraper.caching import cacheable


class SerialeOnlinePl(AntiCaptchaImageMixin, SimpleScraperBase):
    BASE_URL = 'https://www.serialeonline.pl'
    OTHERS_URLS = ['http://www.serialeonline.pl']

    SINGLE_RESULTS_PAGE = True
    LONG_SEARCH_RESULT_KEYWORD = 'the'

    def setup(self):
        self.register_scraper_type(ScraperBase.SCRAPER_TYPE_OSP)

        self.search_term_language = 'pol'

        # self.register_media(ScraperBase.MEDIA_TYPE_FILM)
        self.register_media(ScraperBase.MEDIA_TYPE_TV)

        self.register_url(ScraperBase.URL_TYPE_SEARCH, self.BASE_URL)
        self.register_url(ScraperBase.URL_TYPE_LISTING, self.BASE_URL)

    @cacheable(expire=60 * 60 * 3)
    def __buildlookup(self):
        # Build a dict of show name -> url for the whole site.
        soup = self.get_soup(self.BASE_URL)
        if 'Please enter code in the field below' in soup.text:
            image_url = soup.select_one('div.login-container img')['src']
            key = self.solve_captcha(image_url)
            self.post_soup(self.BASE_URL, data={'code_cap': key})
        lookup = {}
        for mainsoup in self.soup_each([self.BASE_URL, ]):
            for link in mainsoup.select('#allcats .media-heading'):
                lookup[link.text.strip()] = link.parent.href
                lookup[link.text.lower().strip()] = link.parent.href
        return lookup

    def search(self, search_term, media_type, **extra):
        # This site doesn't have a search, so we need to grab everything
        # then simulate the search outselve.s
        lookup = self.__buildlookup()
        search_regex = self.util.search_term_to_search_regex(search_term)
        any_results = False
        for term, page in lookup.items():
            if search_regex.search(term):
                self.submit_search_result(
                    link_url=page,
                    link_title=term,
                )
                any_results = True

        if not any_results:
            self.submit_search_no_results()

    def _parse_parse_page(self, soup):

        for serie_link in soup.select('.panel-collapse.collapse.in .media .media-body .media-heading'):
            video_url = serie_link.parent.href
            serie_soup = self.get_soup(video_url)

            # <img id="gmodal1" data-token="MzMxMjc1MTA3NDMxOA==" onclick="ccc('MzMxMjc1MTA3NDMxOA==');" class="openw_old" style="cursor:pointer;margin-top:-165px;" title="Oglądaj odcinki online!" src="http://www.serialeonline.pl/assets/img/serial-odcinek_06.png">
            # calls
            # function ccc(tk){
            # var url = tk;
            # $("#video").modal('show');
            # $.get(JS_MAIN_DOMAIN + "ajax/em.php?did=" + url + "&trurl=1453233789569e967d25e87&w=0", function(data) {
            #   $('#modalem').html(data);
            # }).success(function() {
            #   $(".embedlista li a").first().click();
            # });

            # http://www.serialeonline.pl/ajax/em.php?did=MzMxMjc1MTA3NDMxOA==&trurl=1453233877569e96d5d21af&w=0

            # Looks like we only need the did - the rest is just junk :)

            # find the watch me link.
            links = serie_soup.select('img#gmodal1')
            for link in links:
                token = link.attrs.get('data-token')
                if not token:
                    raise ScraperParseException('Could not extract token.')
                url = self.BASE_URL + '/ajax/em.php?w=0&did=' + token
                links_soup = self.get_soup(url)

                for funnylnk in links_soup.select('dd.linkplayer'):
                    onclick = funnylnk.attrs.get('onclick')
                    if not onclick:
                        raise ScraperParseException('Could not extract onclick from dd.')
                    season, episode = self.util.extract_season_episode(
                        video_url
                    )
                    for lnk in self.util.find_urls_in_text(onclick):
                        self.submit_parse_result(index_page_title=soup.title.text.strip(),
                                                 link_url=lnk,
                                                 link_title=funnylnk.text,
                                                 series_season=season,
                                                 series_episode=episode,
                                                 )
