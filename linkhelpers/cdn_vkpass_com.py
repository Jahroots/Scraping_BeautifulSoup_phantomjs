import re

from sandcrawler.scraper import ScraperBase

class CdnVkpassCom(ScraperBase):

    TEST_URL = "http://cdn27.vkpass.com/token/bDRXWnLzFjPQ/vkphash/x5srT5ax2fx4BsXTkeWkJ7zwFXmNOF9YWBJ3fs8mv5XlyS3uAAtRR00h2cuhV4NWRsGzzuEUVmx.Jz6JhGT58RffOUt9PSwiP59SaG01SE5VR13FD+uMU22uKgEq2Gw8nDnH6Bo1iXi7ukG.gk3azx3o6NpJKnHH7iMbNIGAAcmLC730wRzWyh7+QEdnXn3gvZ67W7wB3c4i7dlvJygWzcGHt0m23WRE7d.oKOj3xP2caDlcTpz.UNscWCfBps3l%7C4xzXme6pWMlxHQhenoWx8t9RMQZh3x+D6o9umBWJVnQ="

    TEST_RESULTS = [
        "https://redirector.googlevideo.com/videoplayback?requiressl=yes&id=c48336fa2d51ec50&itag=37&source=picasa&cmo=secure_transport%3Dyes&ip=0.0.0.0&ipbits=0&expire=1438735646&sparams=requiressl,id,itag,source,ip,ipbits,expire&signature=BDF455EF541B207C5878FBDE4D5B5865E94CCB83.8EED7BB03825FEAFBA7E8C78DF2BFD3A61EFCA54&key=lh1",
        "https://redirector.googlevideo.com/videoplayback?requiressl=yes&id=c48336fa2d51ec50&itag=22&source=picasa&cmo=secure_transport%3Dyes&ip=0.0.0.0&ipbits=0&expire=1438735646&sparams=requiressl,id,itag,source,ip,ipbits,expire&signature=13C9080AF09EB52821A15EB142D673D79399381F.5811F04B90CB915E5AB8F9CBD9A44D8BD885349E&key=lh1",
        "https://redirector.googlevideo.com/videoplayback?requiressl=yes&id=c48336fa2d51ec50&itag=22&source=picasa&cmo=secure_transport%3Dyes&ip=0.0.0.0&ipbits=0&expire=1438735646&sparams=requiressl,id,itag,source,ip,ipbits,expire&signature=13C9080AF09EB52821A15EB142D673D79399381F.5811F04B90CB915E5AB8F9CBD9A44D8BD885349E&key=lh1"
        "https://redirector.googlevideo.com/videoplayback?requiressl=yes&id=c48336fa2d51ec50&itag=18&source=picasa&cmo=secure_transport%3Dyes&ip=0.0.0.0&ipbits=0&expire=1438735646&sparams=requiressl,id,itag,source,ip,ipbits,expire&signature=352DC32A270E345E9CCF5B3DC92BE0F7818ACD3A.9F5440EA3270F25F57F7D40D01A57AD8DFB20E77&key=lh1"
        ]

    def setup(self):

        self.register_url(ScraperBase.URL_TYPE_AGGREGATE,
            re.compile('http://cdn\d+.vkpass.com'))

    def expand(self, url, **extra):
        links = []
        for content in self.get_each([url,]):
            links += self.util.find_file_in_js(content)
        return links