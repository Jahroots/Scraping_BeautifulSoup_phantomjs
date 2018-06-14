import traceback
import time
import copy
import json


class ScraperExceptionLogger(object):
    _instance = None

    @classmethod
    def create_instance(cls):
        return ScraperExceptionLogger()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.create_instance()

        return cls._instance

    def __init__(self):
        super(ScraperExceptionLogger, self).__init__()

        self.delegate = None

    def exception_created(self, exception):
        if self.delegate and hasattr(self.delegate, 'exception_created'):
            self.delegate.exception_created(exception)


class ScraperException(Exception):
    def __init__(self, msg=None, *args, **kwargs):
        super(ScraperException, self).__init__()
        self.message = msg
        self.data = kwargs
        self.trace = traceback.format_exc()
        self.timestamp = int(time.time())

        self.logged = False  # Marks if the exception has been logged already

        ScraperExceptionLogger.instance().exception_created(self)

    def __str__(self):
        original_error = "<>"
        if 'error' in self.data:
            error = self.data.get('error')

            if isinstance(error, basestring):
                original_error = str(error)
            else:
                original_error = str(type(self.data['error']))

        message_string = (str(self.message), "(None)")[self.message is None]
        exception_name = self.__class__.__name__

        return "{exception_name} '{message_string}' {original_error}".format(**locals())

    def packet(self):
        data = copy.copy(self.data)

        error = data.get('error', None)
        if error:
            del data['error']

        error = str(error)

        packet = dict(type=self.__class__.__name__, message=self.message, trace=self.trace, error=error, data=data, timestamp=self.timestamp)

        return packet

    def json(self):
        return json.dumps(self.packet())


class ScraperFetchException(ScraperException):
    """
    There has been an issue in retrieving a page
    """
    pass


class ScraperFetchProxyException(ScraperException):
    """
    There has likely been some sort of proxy related error in retrieving a page
    """
    pass


class ScraperParseException(ScraperException):
    """
    There has been an issue in parsing page content
    """
    pass


class ScraperAuthException(ScraperParseException):
    """
    There has been an issue with site authentication
    """
    pass