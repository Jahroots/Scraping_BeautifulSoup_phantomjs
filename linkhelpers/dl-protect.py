from sandcrawler.scraper import ScraperBase


class DlProtect(ScraperBase):
    TEST_URL = 'http://www.dl-protect.com/FA4E71A5'
    TEST_RESULTS = ['http://dfiles.ru/files/b6pnv2zln%20%20%20Bjlet.na.Vejas.part1.rar',
                    'http://dfiles.ru/files/awn72qs0e%20%20%20Bjlet.na.Vejas.part2.rar',
                    'http://dfiles.ru/files/y2ta58xah%20%20%20Bjlet.na.Vejas.part3.rar']

    def setup(self):
        raise NotImplementedError('solve captcha')
        self.register_url(ScraperBase.URL_TYPE_AGGREGATE, 'http://www.dl-protect.com')

    def expand(self, url, **extra):
        # TODO

        return
