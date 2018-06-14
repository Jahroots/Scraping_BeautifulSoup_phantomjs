import os
import logging
import getpass
import cookielib


class ScraperSharedState(object):
    def __init__(self, scraper_name):
        super(ScraperSharedState, self).__init__()

        self.log = logging.getLogger(scraper_name + ":"+ self.__class__.__name__)

        self._scraper_name = scraper_name

        self._cookie_jar = None

    def load(self):
        self.log.debug("TODO: Implement loading of state")

    def save(self):
        self.log.debug("TODO: Implement saving of state")

    @property
    def cookie_jar(self):
        if not self._cookie_jar:
            self.log.warning("WARNING: Creating cookie jar")
            self._cookie_jar = cookielib.FileCookieJar()

            filename = "cookies_{0}_{1}.txt".format(getpass.getuser(), self._scraper_name)
            self._cookie_jar.filename = os.path.join("/tmp", filename)

        return self._cookie_jar
