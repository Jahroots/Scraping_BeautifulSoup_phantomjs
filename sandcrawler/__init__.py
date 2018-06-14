# further beautifying the BS

from bs4.element import Tag


@property
def href(self):
    return self.attrs.get('href', '')


Tag.href = href


@property
def startswith_http(self):
    return self.href and (
        self.href.startswith('http:') or self.href.startswith('https:')
    )


Tag.startswith_http = startswith_http
